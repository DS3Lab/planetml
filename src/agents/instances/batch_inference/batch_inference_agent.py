# This handles batch inference jobs
from loguru import logger
from .._base import LocalCoordinator
from typing import Optional
from pydantic import BaseSettings
from src.agents.clients.LSFClient import LSFClient
from src.agents.utils.planetml import PlanetML


class Settings(BaseSettings):
    euler_lsf_host: Optional[str]
    euler_lsf_username: Optional[str]
    euler_lsf_password: Optional[str]
    euler_lsf_wd: Optional[str]
    euler_lsf_init: Optional[str]
    stanford_host: Optional[str]
    stanford_username: Optional[str]
    stanford_password: Optional[str]
    stanford_wd: Optional[str]
    stanford_init: Optional[str]
    stanford_gateway: Optional[str]

    class Config:
        env_file = 'src/agents/.env'
        env_file_encoding = 'utf-8'

machine_size_mapping = {
    'gpt-j-6b': 4,
    'gpt-neox-20b': 11,
    't0pp': 6,
    't5-11b': 6,
    'ul2': 16,
    'stable_diffusion': 1,
    'opt-66b': 8,
    'opt-175b': 8,
    'bloom': 8,
    'yalm': 8,
    'glm': 8,
}

target_cluster_mapping = {
    'gpt-j-6b': 'euler',
    'gpt-neox-20b': 'euler',
    't0pp': 'euler',
    't5-11b': 'euler',
    'ul2': 'euler',
    'stable_diffusion': 'euler',
    'opt-66b': 'stanford',
    'opt-175b': 'stanford',
    'bloom': 'stanford',
    'yalm': 'stanford',
    'glm': 'stanford',
}

settings = Settings()

clients = {
    "euler": LSFClient(
        host=settings.euler_lsf_host,
        username=settings.euler_lsf_username,
        password=settings.euler_lsf_password,
        wd=settings.euler_lsf_wd,
        init=settings.euler_lsf_init,
        infra='lsf',
    ),
    "stanford": LSFClient(
        host=settings.stanford_host,
        username=settings.stanford_username,
        password=settings.stanford_password,
        wd=settings.stanford_wd,
        init=settings.stanford_init,
        gateway=settings.stanford_gateway,
        infra='slurm',
    )
}


class BatchInferenceCoordinator(LocalCoordinator):
    def __init__(self,
                 name,
                 coord_status
                 ) -> None:
        super().__init__(name)
        self.name = "batch_inference"
        self.allocated_index = 0
        self.planetml = PlanetML()
        self.client = None
        self.coord_status = coord_status

    def _allocate_index(self):
        self.allocated_index = (self.allocated_index + 1) % 10000
        return self.allocated_index

    def dispatch(self, job):
        """
        job: fields: machine_size, world_size, infer_data, job_name
        """
        try:
            if 'lsf_script_path' not in job:
                lsf_script_path = 'runner/src/agents/runner/batch_inference/submit_cache'
            else:
                lsf_script_path = job['lsf_script_path']
            job_payload = job['payload']
            if "machine_size" in job_payload[0] and "world_size" in job_payload[0]:
                machine_size, world_size = job_payload[0]["machine_size"], job_payload["world_size"][0]
            elif 'model' in job_payload[0]:
                if job_payload[0]['model'] not in machine_size_mapping:
                    raise ValueError(f"model {job_payload[0]['model']} not supported")
                machine_size, world_size = machine_size_mapping[job_payload[0]['model']], machine_size_mapping[job_payload[0]['model']]
                model_type = job_payload[0]['model']
            else:
                raise ValueError("Cannot understand input!")
            target_cluster = target_cluster_mapping[model_type]
            # now find the rate limit from coord status, we assume all clusters have a rate limit
            logger.info(f"target cluster: {target_cluster}")
            rate_limit = self.coord_status['rate_limit'][target_cluster]
            inqueue_jobs = self.coord_status['inqueue_jobs'][target_cluster]
            logger.info(f"rate limit: {rate_limit}, inqueue jobs: {inqueue_jobs}")
            if len(inqueue_jobs) >= rate_limit:
                logger.info("rate limit reached, waiting for next round")
                return
            logger.info(f"Deploying to cluster: {target_cluster}")
            
            self.client = clients[target_cluster]
            self.client._connect()
            if machine_size < 0 or world_size < 0:
                raise ValueError(
                    f"Invalid machine_size or world_size, expected positive integers, got {machine_size} and {world_size}")
            logger.info("fetching job payload..")
            self.client.execute_raw_in_wd(
                f"cd working_dir && curl -X 'GET' 'https://coordinator.shift.ml/eth/job_payload/{job['id']}' -o input_{job['id']}.json"
            )
            demand_worker_num = machine_size
            for i in range(demand_worker_num):
                logger.info("preparing files")
                result = self.client.execute_raw_in_wd(
                    f"cd {lsf_script_path} && cp ../{job_payload[0]['model']}.{self.client.infra}.jinja ./submit_{i + 1}.bsub")

                print('copied template to submit.bsub')
                if self.client.infra == 'lsf':
                    result = self.client.execute_raw_in_wd(
                        f"cd {lsf_script_path} && ls && echo \'--lsf-job-no {self._allocate_index()} --job_id {job['id']}\' >> submit_{i + 1}.bsub"
                    )
                logger.info(f"submission file for worker {i} is prepared...")
                if self.client.infra == 'lsf':
                    result = self.client.execute_raw_in_wd(
                        f"cd {lsf_script_path} && bsub < submit_{i + 1}.bsub"
                    )
                elif self.client.infra == 'slurm':
                    result = self.client.execute_raw_in_wd(
                        f"cd {lsf_script_path} && sbatch submit_{i + 1}.bsub {job['id']}"
                    )
                job_id = ""
                queue_id = ""
                if self.client.infra == 'lsf':
                    job_id = result.split("<")[1].split(">")[0]
                    queue_id = result.split("<")[2].split(">")[0]
                    logger.info(
                        f"job submitted, job_id: {job_id}, queue_id: {queue_id}")
            self.planetml.update_job_status(
                job_id=job['id'],
                processed_by=f"{job_id}:{queue_id}:{self.client.host}",
                status="queued",
                source=job['source'],
                type=job['type'],
                returned_payload={}
            )
            result = self.client.execute_raw_in_wd(
                f"cd {lsf_script_path} && rm *.bsub"
            )
            return {
                'status': 'queued',
                'model': job_payload[0]['model'],
                'cluster': target_cluster
            }
        except Exception as e:
            self.planetml.update_job_status(
                job_id=job['id'],
                processed_by="",
                status="failed",
                source=job['source'],
                type=job['type'],
                returned_payload={"message": str(e)}
            )
