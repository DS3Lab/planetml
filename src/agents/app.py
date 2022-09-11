# the behavior of this script should be controlled by a config file - which agents should be loaded and supervised, etc. - later later...

from fastapi import FastAPI, Request
from fastapi_utils.tasks import repeat_every
from loguru import logger
from pydantic import BaseSettings
import requests
import sys
import random
import json
from typing import Optional

sys.path.append('./')

from src.agents.utils.planetml import PlanetML
from src.agents.instances.batch_inference.batch_inference_agent import BatchInferenceCoordinator

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

lc_app = FastAPI(debug=True, docs_url="/eth/docs",openapi_url="/eth/api/v1/openapi.json")

watched_jobs = {}
watched_ports = {}
job_payload = {}
warmness_of_models = {
    
}
settings = Settings()
submit_lock = False

planetml_client = PlanetML()

def preprocess_job(job):
    if 'url' in job['payload']:
        res = requests.get(job['payload']['url']).text.strip()
        req_payload_from_file = [json.loads(x) for x in res.split("\n")]
        job['payload'] = req_payload_from_file
    else:
        job['payload'] = [job['payload']] if type(job['payload']) != list else job['payload']
    return job

@lc_app.get("/eth/heartbeat/:id")
async def root():
    return {"message": "ok"}


@lc_app.get("/eth/health")
async def health():
    return {"message": "ok"}


@lc_app.post("/eth/node_join")
async def node_join():
    return {"message": "ok"}


@lc_app.post("/eth/rank/{job_id}")
async def post_rank(job_id, req: Request):
    """
    req: {"ip":"xxx"}
    """
    if job_id not in watched_jobs:
        # randomly generate a port
        port = random.randint(10000, 60000)
        job_info = await req.json()
        watched_ports[job_id] = port
        watched_jobs[job_id] = [job_info]
    else:
        job_info = await req.json()
        watched_jobs[job_id].append(await req.json())
    return {
        "prime_ip": watched_jobs[job_id][0]['ip'],
        "rank": len(watched_jobs[job_id])-1,
        "nccl_port": watched_ports[job_id],
    }

@lc_app.post("/eth/update_status/{id}")
async def update_status(id, req: Request):
    request_json = await req.json()
    if request_json['returned_payload']:
        if request_json['status'] == 'finished':
            print(request_json['returned_payload'])
            # upload results to S3
            result_files = planetml_client.write_json_to_s3(request_json['returned_payload'])
            res = planetml_client.update_job_status(
                id,
                status=request_json['status'],
                returned_payload=result_files,
                type="general",
                source='dalle'
            )
        else:
            res = planetml_client.update_job_status(
                id,
                status=request_json['status'],
                returned_payload=request_json['returned_payload'],
                type="general",
                source='dalle'
            )
    else:
        res = planetml_client.update_job_status(
            id,
            status=request_json['status'],
            type="general",
            source='dalle'
        )
    return res

@lc_app.get("/eth/job_payload/{job_id}")
async def get_job_payload(job_id):
    return job_payload[job_id]

@lc_app.on_event("startup")
@repeat_every(seconds=10)  # fetch jobs every $ seconds， but check submit lock
def fetch_submitted_jobs():
    global submit_lock
    if not submit_lock:
        try:
            logger.info("Fetching and dispatching jobs")
            jobs = planetml_client.get_jobs()
            bi_jobs = [x for x in jobs 
                if x['source'] == 'dalle' \
                    and x['status'] == 'submitted' \
                        and x['type'] == 'general'
            ]
            logger.info("Found {} jobs batch inference".format(len(bi_jobs)))
            if len(bi_jobs) > 0:
                bi_coordinator = BatchInferenceCoordinator(
                   "batch_inference"
                )
            for each in bi_jobs:
                # acquire submit lock
                submit_lock = True
                try:
                    each = preprocess_job(each)
                except Exception as e:
                    planetml_client.update_job_status(
                        job_id=each['id'],
                        processed_by="",
                        status="failed",
                        source=each['source'],
                        type=each['type'],
                        returned_payload={"message": str(e)}
                    )
                job_payload[each['id']] = each['payload']
                bi_coordinator.dispatch(each)
            # release submit lock
            submit_lock = False
        except Exception as e:
            submit_lock = False
            logger.error(e)
            raise e.with_traceback()
    else:
        logger.info("Submit lock is on, skipping this round")