from typing import OrderedDict

from src.agents.clients.LSFClient import LSFClient
from .._base import LocalCoordinator
from pydantic import BaseSettings


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
        
        self.client = LSFClient(
            host=settings.lsf_host,
            username=settings.lsf_username,
            password=settings.lsf_password,
            wd=settings.lsf_wd,
            init=settings.lsf_init,
        )

    def dispatch(self, job):
        """
        job: fields: machine_size, world_size, infer_data, job_name
        """
        if not self.submit_lock:
            self.submit_lock = True
        machine_size, world_size = job["machine_size"], job["world_size"]
        if machine_size < 0 or world_size < 0:
            raise ValueError(
                f"Invalid machine_size or world_size, expected positive integers, got {machine_size} and {world_size}")

        demand_worker_num = machine_size

        for i in range(demand_worker_num):
            # generate bsub file on the fly
            self.client.execute(
                f"echo \'--lsf-job-no {self._allocate_index()} --infer-data {job['infer_data']}\' >> {settings().lsf_init}/submit_cache/{job['job_name']}_{i + 1}.bsub")
            result = self.client.execute(
                f"cd {settings().lsf_init}/submit_cache/ && && bsub < {job['job_name']}_{i + 1}.bsub"
            )
            job_id = result.split("<")[1].split(">")[0]
            queue_id = result.split("<")[2].split(">")[0]