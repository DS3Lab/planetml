"""
This bot is used to consume tasks published to the queue, but only with the source=dataperf.
It handles valid mlsphere configuration, runs the pipeline defined in the configuration and returns the results.
"""
import typer
import requests
from pydantic import BaseSettings
from clients.LSFClient import LSFClient
from rest.rest import update_job_status

planetml_url = 'https://planetd.shift.ml/jobs'

agent = typer.Typer()

class Settings(BaseSettings):
    lsf_host: str
    lsf_username: str
    lsf_password: str
    lsf_wd: str
    lsf_init: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


def dispatch_job(job):
    typer.echo(f"Dispatching job {job['id']}")
    settings = Settings()
    lsf_client = LSFClient(
        host=settings.lsf_host,
        username=settings.lsf_username,
        password=settings.lsf_password,
        wd=settings.lsf_wd,
        init=settings.lsf_init,
    )
    lsf_client.execute(
        f"rm -rf {job['payload']['submission_id']}"
    )
    lsf_client.execute(
        f"mkdir {job['payload']['submission_id']} && cd {job['payload']['submission_id']} && wget {job['payload']['url']} -O {job['payload']['submission_id']}.zip && unzip {job['payload']['submission_id']}.zip && rm {job['payload']['submission_id']}.zip"
    )
    image_path = "/nfs/iiscratch-zhang.inf.ethz.ch/export/zhang/export/xiayao/projects/dataperf/images/"
    results = lsf_client.execute(f"cd {job['payload']['submission_id']} && bsub /cluster/home/xiayao/.local/bin/mls.py run create_baselines {image_path}")
    
    job_id = results.split("<")[1].split(">")[0]
    queue_id = results.split("<")[2].split(">")[0]
    res = update_job_status(job['id'], processed_by=f'{job_id}:{queue_id}:euler.ethz.ch', status='queued')
    print(res.text)
    typer.echo(f"Job {job['id']} dispatched on queue {queue_id} with euler job id {job_id}")

@agent.command()
def fetch():
    """
    Fetch jobs
    """
    response = requests.get(planetml_url).json()
    submitted_jobs = [x for x in response if x['status'] == 'submitted']
    typer.echo(f"Found {len(submitted_jobs)} jobs")
    for each in submitted_jobs:
        dispatch_job(each)


if __name__ == "__main__":
    agent()
