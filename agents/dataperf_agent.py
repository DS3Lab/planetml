"""
This bot is used to consume tasks published to the queue, but only with the source=dataperf.
It handles valid mlsphere configuration, runs the pipeline defined in the configuration and returns the results.
"""
import json
import typer
import requests
from pydantic import BaseSettings
from clients.LSFClient import LSFClient
from rest.rest import update_job_status
import time
from loguru import logger
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

def dispatch_job(lsf_client, job):
    typer.echo(f"Dispatching job {job['id']}")
    lsf_client.execute(
        f"rm -rf {job['payload']['submission_id']}"
    )
    lsf_client.execute(
        f"mkdir {job['payload']['submission_id']} && cd {job['payload']['submission_id']} && wget {job['payload']['url']}?t=1234 -O {job['payload']['submission_id']}.zip && unzip {job['payload']['submission_id']}.zip && rm {job['payload']['submission_id']}.zip"
    )
    image_path = "/nfs/iiscratch-zhang.inf.ethz.ch/export/zhang/export/xiayao/projects/dataperf/images/"
    results = lsf_client.execute(f"cd {job['payload']['submission_id']} && bsub -R singularity -n 32 /cluster/home/xiayao/.local/bin/mls.py run-pipeline --image-path {image_path}")
    
    job_id = results.split("<")[1].split(">")[0]
    queue_id = results.split("<")[2].split(">")[0]
    res = update_job_status(job['id'], processed_by=f'{job_id}:{queue_id}:euler.ethz.ch', status='queued')
    print(res.text)
    typer.echo(f"Job {job['id']} dispatched on queue {queue_id} with euler job id {job_id}")
    return f'{job_id}:{queue_id}:euler.ethz.ch'

def check_job_status(lsf_client):
    results = lsf_client.execute_raw("bjobs -json -o 'jobid stat queue'")
    records = json.loads(results)
    return records['RECORDS']


@agent.command()
def fetch():
    """
    Fetch jobs
    """
    response = requests.get(planetml_url).json()
    submitted_jobs = [x for x in response if x['status'] == 'submitted']
    settings = Settings()
    lsf_client = LSFClient(
        host=settings.lsf_host,
        username=settings.lsf_username,
        password=settings.lsf_password,
        wd=settings.lsf_wd,
        init=settings.lsf_init,
    )
    typer.echo(f"Found {len(submitted_jobs)} jobs")
    for each in submitted_jobs:
        dispatch_job(lsf_client, each)
    check_job_status(lsf_client)

@agent.command()
def watch():
    typer.echo("Watching for new jobs")
    watch_job_map = {}
    while True:
        response = requests.get(planetml_url).json()
        submitted_jobs = [x for x in response if x['status'] == 'submitted']
        settings = Settings()
        lsf_client = LSFClient(
            host=settings.lsf_host,
            username=settings.lsf_username,
            password=settings.lsf_password,
            wd=settings.lsf_wd,
            init=settings.lsf_init,
        )
        typer.echo(f"Found {len(submitted_jobs)} jobs")
        for each in submitted_jobs:
            processed_by = dispatch_job(lsf_client, each)
            watch_job_map[each['id']] = {
                'processed_by': processed_by,
                'status': 'queued'
            }
        status_records = check_job_status(lsf_client)
        for each_record in status_records:
            processed_by = f"{each['JOBID']}:{each['QUEUE']}:euler.ethz.ch"
            still_running = False
            job_id = None
            for each in watch_job_map:
                new_status = ""
                if watch_job_map[each]['processed_by'] == processed_by:
                    still_running = True
                    job_id = each
                    if each['status'] == "RUN":
                        new_status='running'
                    elif each['status'] == "PEND":
                        new_status='queued'

            if still_running and new_status != 'queued':
                typer.echo(f"Updating job {job_id} to {new_status}")
                update_job_status(job_id, processed_by=processed_by, status=new_status)
            else:
                typer.echo(f"Updating job {job_id} to completed")
                res = update_job_status(job_id, processed_by=processed_by, status='finished')
                print(res.text)
        typer.echo(f"Sleeping for 10 seconds")
        time.sleep(10)

if __name__ == "__main__":
    agent()