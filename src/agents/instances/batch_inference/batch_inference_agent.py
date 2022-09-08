# This handles batch inference jobs
from loguru import logger
from .._base import LocalCoordinator

from src.agents.clients.LSFClient import LSFClient
from src.agents.utils.planetml import PlanetML

machine_size_mapping = {
    'gpt_j_6B': 2,
    'gpt_neox': 8,
    't0_pp': 6,
    't5': 6,
    'ul2': 16,
    'opt_66B': 8,
}

class BatchInferenceCoordinator(LocalCoordinator):
    def __init__(self,
                 name,
                 client: LSFClient,
                 ) -> None:
        super().__init__(name)
        self.name = "batch_inference"
        self.allocated_index = 0
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
        job_payload = job['payload']
        logger.info("job_payload: {}", job_payload[0])
        
        if "machine_size" in job_payload[0] and "world_size" in job_payload[0]:
            machine_size, world_size = job_payload[0]["machine_size"], job_payload["world_size"][0]
        elif "model" in job_payload[0]:
            logger.warning("Using default parameters for machine_size=1 and world_size=1")
            machine_size = 1
            world_size = 1
        else:
            machine_size, world_size = machine_size_mapping[job_payload[0]['engine']], machine_size_mapping[job_payload[0]['engine']]

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
            if 'model' in job_payload[0]:
                result = self.client.execute_raw_in_wd(f"cd {lsf_script_path} && cp ../{job_payload[0]['model']}.{self.client.infra}.jinja ./submit_{i + 1}.bsub")
            else:
                result = self.client.execute_raw_in_wd(f"cd {lsf_script_path} && cp ../{job_payload[0]['engine']}.{self.client.infra}.jinja ./submit_{i + 1}.bsub")
            print('copied template to submit.bsub')
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
                    f"cd {lsf_script_path} && sbatch submit_{i + 1}.bsub"
                )
            job_id = ""
            queue_id = ""
            if self.client.infra == 'lsf':
                job_id = result.split("<")[1].split(">")[0]
                queue_id = result.split("<")[2].split(">")[0]
                logger.info(f"job submitted, job_id: {job_id}, queue_id: {queue_id}")
            self.planetml.update_job_status(
                job_id=job['id'],
                processed_by=f"{job_id}:{queue_id}:{self.client.host}",
                status="queued",
                source=job['source'],
                type=job['type'],
                returned_payload={}
            )