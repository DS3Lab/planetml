
"""
This bot is used to consume tasks published to the queue, but only with the source=dataperf.
It handles valid mlsphere configuration, runs the pipeline defined in the configuration and returns the results.
"""
import time
import json
import typer
import requests
from pydantic import BaseSettings
from clients.LSFClient import LSFClient
from src.agents.utils.planetml import update_job_status
from utils.pprint import print_table

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
    
    results = lsf_client.execute(f"cd {job['payload']['submission_id']} && bsub -R singularity -n 16 /cluster/home/xiayao/.local/bin/mls.py run-pipeline --image-path {image_path}")
    
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

def harvest_finished_run(lsf_client, job_id, submission_id, euler_job_id):
    typer.echo(f"Checking is job is done successfully")
    # now check if the job is done successfully
    is_successful = lsf_client.is_successful(submission_id, euler_job_id)
    if is_successful:
        lsf_client.execute(f"cd {lsf_client.wd}/{submission_id} && /cluster/home/xiayao/.local/bin/mls.py upload-results --bucket dataperf-results --filename {submission_id}")
        typer.echo(f"Updating job {job_id} to finished")
        update_job_status(job_id, processed_by=f"{euler_job_id}:euler.ethz.ch", status='finished')
    else:
        typer.echo(f"Updating job {job_id} to failed")
        update_job_status(job_id, processed_by=f"{euler_job_id}:euler.ethz.ch", status='failed')

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
        # Dispatching new jobs
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
                'status': 'queued',
                'submission_id': each['payload']['submission_id']
            }
        # check jobs status
        status_records = check_job_status(lsf_client)
        if len(status_records) > 0:
            print_table(status_records, title="Jobs Status")
            
        for each_record in status_records:
            processed_by = f"{each_record['JOBID']}:{each_record['QUEUE']}:euler.ethz.ch"
            still_running = False
            job_id = None
            for each in watch_job_map:
                new_status = ""
                if watch_job_map[each]['processed_by'] == processed_by:
                    still_running = True
                    job_id = each
                    if each_record['STAT'] == "RUN":
                        new_status='running'
                    elif each_record['STAT'] == "PEND":
                        new_status='queued'

            if job_id is not None:
                if still_running and new_status != 'queued':
                    typer.echo(f"Updating job {job_id} to {new_status}")
                    update_job_status(job_id, processed_by=processed_by, status=new_status)
        # harvest finished runs
        for each in watch_job_map.copy():
            processed_by = watch_job_map[each]['processed_by']
            euler_jobid = processed_by.split(":")[0]
            running_jobs = [x['JOBID'] for x in status_records]
            if euler_jobid not in running_jobs:
                typer.echo(f"Harvesting job {each}")
                harvest_finished_run(lsf_client,each, watch_job_map[each]['submission_id'], euler_jobid)
                del watch_job_map[each]
        
        typer.echo(f"Sleeping for 30 seconds")
        time.sleep(30)

if __name__ == "__main__":
    agent()