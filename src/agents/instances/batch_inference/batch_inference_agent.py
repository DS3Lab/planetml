# This handles batch inference jobs

from typing import OrderedDict
from pydantic import BaseSettings
from loguru import logger

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
        self.submit_lock = False
        self.client = LSFClient(
            host=settings.euler_lsf_host,
            username=settings.euler_lsf_username,
            password=settings.euler_lsf_password,
            wd=settings.euler_lsf_wd,
            init=settings.euler_lsf_init,
        )
        self.client._connect()

    def _allocate_index(self):
        self.allocated_index = (self.allocated_index + 1) % 10000
        return self.allocated_index

    def dispatch(self, job):
        """
        job: fields: machine_size, world_size, infer_data, job_name
        """
        logger.info(f"dispatching job {job}")
        if not self.submit_lock:
            self.submit_lock = True
        job_payload = job['payload']
        machine_size, world_size = job_payload["machine_size"], job_payload["world_size"]
        if machine_size < 0 or world_size < 0:
            raise ValueError(
                f"Invalid machine_size or world_size, expected positive integers, got {machine_size} and {world_size}")

        demand_worker_num = machine_size
        for i in range(demand_worker_num):
            # generate bsub file on the fly
            result = self.client.execute("ls")
            print(result)
            result = self.client.execute(
                f"cd {settings().lsf_init}/batch_inference/submit_cache/ && && bsub < {job['job_name']}_{i + 1}.bsub"
            )
            print(result)
            job_id = result.split("<")[1].split(">")[0]
            queue_id = result.split("<")[2].split(">")[0]