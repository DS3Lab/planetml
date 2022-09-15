# the behavior of this script should be controlled by a config file - which agents should be loaded and supervised, etc. - later later...

import sys
import time
import json
import random
import requests
from loguru import logger
from typing import Optional
from pydantic import BaseSettings
from fastapi import FastAPI, Request
from fastapi_utils.tasks import repeat_every
from datetime import datetime
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


lc_app = FastAPI(debug=True, docs_url="/eth/docs",
                 openapi_url="/eth/api/v1/openapi.json")
# sooner or later, this will be synced with the global coordinator/local database, such that it can be resumed if the local coordinator is restarted
job_status = {}
watched_jobs = {}
watched_ports = {}
job_payload = {}
model_warmness = {}
model_instructions = {}
model_heartbeats = {}
example_jobs = {
    'stable_diffusion': {
        "type": "general",
        "payload": {
            "model": "stable_diffusion",
            "num_returns": 1,
            "input": [
                "Painting of a hippo"
            ]
        },
        "returned_payload": {},
        "status": "submitted",
        "source": "dalle",
        "processed_by": ""
    }
}
settings = Settings()
submit_lock = False
planetml_client = PlanetML()

coord_status = {
    'health': 'ok',
    'jobs': {},
    'models': {
        'warmness': {},
        'instructions': {},
        'heartbeats': {}
    },
    'minimal_warmness': {
        'stable_diffusion': 1
    }
}


def preprocess_job(job):
    is_interactive = True
    if 'url' in job['payload']:
        res = requests.get(job['payload']['url']).text.strip()
        req_payload_from_file = [json.loads(x) for x in res.split("\n")]
        job['payload'] = req_payload_from_file
        is_interactive = False
    else:
        job['payload'] = [job['payload']] if type(
            job['payload']) != list else job['payload']
    return job, is_interactive


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
    # here we update instructions and heartbeats
    # if this job is in the list of instructions, we update the instructions such that the job is removed from the database
    for model_name in model_instructions:
        instructions = model_instructions[model_name]
        for instruction in instructions:
            if instruction['message'] == 'run':
                if instruction['payload']['id'] == id:
                    instruction['payload']['status'] = request_json['status']

    if request_json['returned_payload']:
        if request_json['status'] == 'finished':
            # upload results to S3
            result_files = planetml_client.write_json_to_s3(
                request_json['returned_payload'])
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


@lc_app.get("/eth/warmness/{model_name}")
async def get_model_warmness(model_name):
    if model_name in model_warmness:
        warmness = model_warmness[model_name]
    else:
        warmness = 0
    return {"warmness": warmness, 'message': 'ok'}


@lc_app.get("/eth/warmnesses")
async def get_all_warmness():
    return {"warmness": model_warmness, 'message': 'ok'}


@lc_app.get("/eth/instructions/{model_name}")
async def get_instruction(model_name):
    # tell global coordinator that this model is alive
    planetml_client.update_model_status(model=model_name, payload={
        "warmness": 1,
        "last_heartbeat": datetime.utcnow()
    })
    if model_name not in model_instructions:
        # at this moment, the worker is asking for instructions of a model, so it is ready to accept jobs
        # we can set the warmness of the model to be 1
        model_warmness[model_name] = 1
        model_instructions[model_name] = [{"message": "continue"}]
    elif model_warmness[model_name] < 1:
        model_warmness[model_name] = 1
    model_heartbeats[model_name] = time.time()
    return model_instructions[model_name]


@lc_app.on_event("shutdown")
def shutdown_event():
    logger.info("dumping results to local db...")


def update_warmnesses():
    logger.info("updating warmnesses...")

    for model_name in model_heartbeats:
        if time.time() - model_heartbeats[model_name] > 60:
            # now this model is not warm anymore, we do the following
            # set it's warmness to 0
            model_warmness[model_name] = 0
            # tell global coordinator that this model is not warm anymore
            planetml_client.update_model_status(model=model_name, payload={
                "warmness": 0,
                "last_heartbeat": ""
            })
        # now check model warmness again - if it is not warm, but there is a limitation specified in coord_status['minimal_warmness'], we starts a test job

    for model_name in coord_status['minimal_warmness']:
        if model_name in model_warmness:
            if model_warmness[model_name] >= 0.5:
                logger.info(
                    f"{model_name} is being warmed up or is warmed, skipping...")
                continue
        if model_name not in model_warmness and coord_status['minimal_warmness'][model_name] >= 1:
            logger.info(f"dispatching a warming job for model {model_name}")
            requests.post("https://planetd.shift.ml/jobs",
                          json=example_jobs[model_name])
            model_warmness[model_name] = 0.5
            # add 3 minutes buffer to the heartbeats
            model_heartbeats[model_name] = time.time() + 180
        elif model_warmness[model_name] < coord_status['minimal_warmness'][model_name]:
            # means we need to start a test job
            logger.info(f"dispatching a warming job for model {model_name}")
            requests.post("https://planetd.shift.ml/jobs",
                          json=example_jobs[model_name])
            model_warmness[model_name] = 0.5
            # add 3 minutes buffer to the heartbeats
            model_heartbeats[model_name] = time.time() + 180


def fetch_submitted_jobs():
    global submit_lock
    if not submit_lock:
        try:
            logger.info("Fetching and dispatching jobs")
            jobs = planetml_client.get_jobs()
            bi_jobs = [x for x in jobs
                       if x['source'] == 'dalle'
                       and x['status'] == 'submitted'
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
                    each, is_interactive = preprocess_job(each)
                except Exception as e:
                    submit_lock = False
                    planetml_client.update_job_status(
                        job_id=each['id'],
                        processed_by="",
                        status="failed",
                        source=each['source'],
                        type=each['type'],
                        returned_payload={"message": str(e)}
                    )
                    return
                # here if it is a file, i.e., url is provided, we regard it as a batch inference job
                # otherwise, it is an interactive job - we will dispatch it to a live coordinator
                # if no live coordinator is available, we will create a new one
                if not is_interactive or not each['payload'][0]['model'] in model_warmness:
                    # it's not an interactive job, or the model is not warm,
                    # dispatch it to a cluster

                    job_payload[each['id']] = each['payload']
                    dispatch_result = bi_coordinator.dispatch(each)
                else:
                    # for interactive job
                    # first check warmness
                    # put it into instructions list
                    if model_warmness[each['payload'][0]['model']] >= 1:
                        if each['payload'][0]['model'] not in model_instructions:
                            model_instructions[each['payload'][0]['model']] = [
                                {"message": "continue"}]
                        model_instructions[each['payload'][0]['model']].append({
                            "message": "run",
                            "payload": each
                        })
                    else:
                        # this model is warm in the past, but not now
                        job_payload[each['id']] = each['payload']
                        dispatch_result = bi_coordinator.dispatch(each)
            # release submit lock
            submit_lock = False
        except Exception as e:
            submit_lock = False
            logger.error(e)
            raise e.with_traceback()
    else:
        logger.info("Submit lock is on, skipping this round")
    # in any case, we need to update warmnesses


@lc_app.on_event("startup")
@repeat_every(seconds=10)  # fetch jobs every $ seconds， but check submit lock
def periodical():
    fetch_submitted_jobs()
    update_warmnesses()