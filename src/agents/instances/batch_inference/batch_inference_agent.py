# This handles batch inference jobs

from typing import OrderedDict
from pydantic import BaseSettings
from loguru import logger
import json
from src.agents.clients.LSFClient import LSFClient
from .._base import LocalCoordinator


class Settings(BaseSettings):
    euler_lsf_host: str
    euler_lsf_username: str
    euler_lsf_password: str
    euler_lsf_wd: str
    euler_lsf_init: str

    class Config:
        env_file = 'src/agents/.env'
        env_file_encoding = 'utf-8'

settings = Settings()

class BatchInferenceCoordinator(LocalCoordinator):
    def __init__(self,
                 name
                 ) -> None:
        super().__init__(name)
        self.name = "batch_inference"
        self.rank_to_be_allocated = set()
        self.worker_nodes = OrderedDict()
        self.prime_worker_ip = None
        self.jobs = []
        self.allocated_index = 0
        self.submit_lock = False
        self.client = LSFClient(
            host=settings.euler_lsf_host,
            username=settings.euler_lsf_username,
            password=settings.euler_lsf_password,
            wd=settings.euler_lsf_wd,
            init=settings.euler_lsf_init,
        )
        

    def _allocate_index(self):
        self.allocated_index = (self.allocated_index + 1) % 10000
        return self.allocated_index

    def dispatch(self, job):
        self.client._connect()
        """
        job: fields: machine_size, world_size, infer_data, job_name
        """
        logger.info(f"dispatching job {job}")
        if not self.submit_lock:
            logger.info("acquiring submit lock")
            self.submit_lock = True
        job_payload = job['payload']
        if "machine_size" in job_payload and "world_size" in job_payload:
            machine_size, world_size = job_payload["machine_size"], job_payload["world_size"]
        else:
            logger.warning("Using default parameters for machine_size=1 and world_size=1")
            machine_size = 1
            world_size = 1
        
        if machine_size < 0 or world_size < 0:
            raise ValueError(
                f"Invalid machine_size or world_size, expected positive integers, got {machine_size} and {world_size}")
        print('start to prepare files')
        # place payload in a file
        job_payload['_id'] = job['id']
        job_payload_str = json.dumps(job_payload)
        self.client.execute_raw_in_wd(
            f"cd working_dir/{job_payload['model']} && echo \'{job_payload_str}\' > input_{job['id']}.json"
        )
        
        demand_worker_num = machine_size
        for i in range(demand_worker_num):
            result = self.client.execute_raw_in_wd(f"cd runner/src/agents/runner/batch_inference/submit_cache && cp ../submission_template.jinja ./submit_{i+1}.bsub")
            print('copied template to submit.bsub')
            result = self.client.execute_raw_in_wd(f"cd runner/src/agents/runner/batch_inference/submit_cache && ls && echo \'--lsf-job-no {self._allocate_index()} --job_id {job['id']}\' >> submit_{i + 1}.bsub")

            logger.info(f"submission file for worker {i} is prepared...")
            result = self.client.execute_raw_in_wd(
                f"cd runner/src/agents/runner/batch_inference/submit_cache && bsub < submit_{i + 1}.bsub"
            )
            job_id = result.split("<")[1].split(">")[0]
            queue_id = result.split("<")[2].split(">")[0]
            logger.info(f"job submitted, job_id: {job_id}, queue_id: {queue_id}")

    def check_job_status(lsf_client):
        results = lsf_client.execute_raw("bjobs -json -o 'jobid stat queue'")
        records = json.loads(results)
        return records['RECORDS']

    def harvest_finished_run(lsf_client, job_id, submission_id, euler_job_id):
        pass