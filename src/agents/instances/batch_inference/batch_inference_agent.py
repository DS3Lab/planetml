from typing import OrderedDict

from src.agents.clients.LSFClient import LSFClient
from .._base import LocalCoordinator

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

    def dispatch(self, job, client: LSFClient):
        if not self.submit_lock:
            self.submit_lock = True
        machine_size, world_size = job["machine_size"], job["world_size"]
        if machine_size < 0 or world_size < 0:
            raise ValueError(f"Invalid machine_size or world_size, expected positive integers, got {machine_size} and {world_size}")
        
        demand_worker_num = machine_size

        
        for i in range(demand_worker_num):
            # generate bsub file on the fly
            pass