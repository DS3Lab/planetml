# This handles batch inference jobs

from typing import OrderedDict
from pydantic import BaseSettings
from loguru import logger
import json
from .._base import LocalCoordinator

from src.agents.clients.LSFClient import LSFClient
from src.agents.utils.planetml import PlanetML


class BatchInferenceCoordinator(LocalCoordinator):
    def __init__(self,
                 name,
                 client: LSFClient,
                 ) -> None:
        super().__init__(name)
        self.name = "batch_inference"
        self.allocated_index = 0
        self.watch_job_map = {}
        self.planetml = PlanetML()
        self.client = client

    def _allocate_index(self):
        self.allocated_index = (self.allocated_index + 1) % 10000
        return self.allocated_index

    def dispatch(self, job):

        """
        job: fields: machine_size, world_size, infer_data, job_name
        """
        if 'lsf_script_path' not in job:
            lsf_script_path = 'runner/src/agents/runner/batch_inference/submit_cache'
        else:
            lsf_script_path = job['lsf_script_path']
        logger.info(f"dispatching job {job}")
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
        # place payload in a file
        job_payload['_id'] = job['id']
        job_payload_str = json.dumps(job_payload)

        self.client.execute_raw_in_wd(
            f"cd working_dir/{job_payload['model']} && echo \'{job_payload_str}\' > input_{job['id']}.json"
        )
        demand_worker_num = machine_size
        for i in range(demand_worker_num):
            logger.info("preparing files")
            result = self.client.execute_raw_in_wd(
                f"cd {lsf_script_path} && cp ../{job_payload['model']}.jinja ./submit_{i + 1}.bsub")
            print('copied template to submit.bsub')
            result = self.client.execute_raw_in_wd(
                f"cd {lsf_script_path} && ls && echo \'--lsf-job-no {self._allocate_index()} --job_id {job['id']}\' >> submit_{i + 1}.bsub")

            logger.info(f"submission file for worker {i} is prepared...")
            result = self.client.execute_raw_in_wd(
                f"cd {lsf_script_path} && bsub < submit_{i + 1}.bsub"
            )
            job_id = result.split("<")[1].split(">")[0]
            queue_id = result.split("<")[2].split(">")[0]
            logger.info(f"job submitted, job_id: {job_id}, queue_id: {queue_id}")
            self.watch_job_map[job['id']] = {
                "processed_by": f"{job_id}:{queue_id}:euler.ethz.ch",
                "status": "queued",
                "job_data": job,
            }
            self.planetml.update_job_status(
                job_id=job['id'],
                processed_by=f"{job_id}:{queue_id}:euler.ethz.ch",
                status="queued",
                source=job['source'],
                type=job['type'],
                returned_payload={}
            )

    def check_job_status(self):
        results = self.client.execute_raw("bjobs -json -o 'jobid stat queue'")
        records = json.loads(results)
        return records['RECORDS']