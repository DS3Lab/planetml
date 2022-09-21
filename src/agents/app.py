# the behavior of this script should be controlled by a config file - which agents should be loaded and supervised, etc. - later later...
import sys
import json
import random
import requests
from loguru import logger
from typing import Optional
from datetime import datetime
from pydantic import BaseSettings
from fastapi import FastAPI, Request
from fastapi_utils.tasks import repeat_every
import traceback

sys.path.append('./')
from src.agents.instances.batch_inference.batch_inference_agent import BatchInferenceCoordinator
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

lc_app = FastAPI(debug=True, docs_url="/eth/docs",
                 openapi_url="/eth/api/v1/openapi.json")
# sooner or later, this will be synced with the global coordinator/local database, such that it can be resumed if the local coordinator is restarted
machine_size_mapping = {
    'gpt-j-6b': 4,
    'stable_diffusion':1
}

job_status = {}
watched_jobs = {}
known_jobs_data = {

}
watched_ports = {}
job_payload = {}
model_warmness = {}
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
    },
    'gpt-j-6b': {
        "type": "general",
        "payload": {
                "best_of": 1,
                "logprobs": 1,
                "max_tokens": 140,
                "n": 1,
                "temperature": 0,
                "top_p": 1,
                "stop": [
                    "\n",
                    "\n\n"
                ],
                "model": "gpt-j-6b",
                "prompt": [
                    "The return value of window.open() is a reference to the newly created window or tab or null if it failed. Do not add a third parameter to it as it will result in the opening of a new window rather than a tab"
                ],
                "request_type": "language-model-inference",
                "echo": False
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
counter_instructions = {}
coord_status = {
    'health': 'ok',
    'models': {
        'warmness': {},
        'instructions': {},
        'heartbeats': {}
    },
    'minimal_warmness': {
        'stable_diffusion': 1,
        'gpt-j-6b': 1
    },
    'inqueue_jobs': {
        'stanford': [
           
        ],
        'euler': [],
        'toma': []
    },
    'rate_limit': {
        'stanford': 3,
        'euler': 9999,
        'toma':999,
    },
    'warm_watch': [
        'gpt-j-6b',
        'stable_diffusion',
    ],
    'known_jobs': []
}


def update_instructions():
    logger.info("updating instructions")
    for model in coord_status['models']['instructions']:
        for instruction in coord_status['models']['instructions'][model]:
            if instruction['message'] == 'run':
                payload_status = instruction['payload']['status']
                if payload_status == 'finished' or payload_status == 'failed':
                    coord_status['models']['instructions'][model].remove(
                        instruction)


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

@lc_app.get("/eth/health")
async def health():
    return {"message": "ok"}

@lc_app.get("/eth/remove_inqueue_jobs/{job_id}")
async def remove_inqueue_jobs(job_id):
    for cluster in coord_status['inqueue_jobs']:
        if job_id in coord_status['inqueue_jobs'][cluster]:
            coord_status['inqueue_jobs'][cluster].remove(job_id)


@lc_app.post("/eth/node_join")
async def node_join():
    return {"message": "ok"}


@lc_app.get("/eth/status")
async def get_coord_status():
    return coord_status

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
    # first release the inqueue job, if the new status is either failed/finished
    if request_json['status'] in ['failed', 'finished']:
        # delete the job from the inqueue list
        if id in coord_status['inqueue_jobs']['stanford']:
            coord_status['inqueue_jobs']['stanford'].remove(id)
        elif id in coord_status['inqueue_jobs']['euler']:
            coord_status['inqueue_jobs']['euler'].remove(id)
        # delete the job from the known_jobs:
        if id in coord_status['known_jobs']:
            coord_status['known_jobs'].remove(id)
            del known_jobs_data[id]

    # here we update instructions and heartbeats
    # if this job is in the list of instructions, we update the instructions such that the job is removed from the database
    for model_name in coord_status['models']['instructions']:
        instructions = coord_status['models']['instructions'][model_name]
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
    if model_name in coord_status['models']['warmness']:
        warmness = coord_status['models']['warmness'][model_name]
    else:
        warmness = 0
    return {"warmness": warmness, 'message': 'ok'}


@lc_app.get("/eth/warmnesses")
async def get_all_warmness():
    return {"warmness": coord_status['models']['warmness'], 'message': 'ok'}


@lc_app.get("/eth/instructions/{model_name}/{rank_id}/{counter}")
async def get_instruction(model_name, rank_id, counter=0):
    counter = int(counter)
    current_time = datetime.utcnow()
    # first check if model_name is in the list of heartbeats
    if model_name not in coord_status['models']['heartbeats']:
        coord_status['models']['heartbeats'][model_name] = {}
        coord_status['models']['warmness'][model_name] = 0

    # put the rank_id into the heartbeats
    coord_status['models']['heartbeats'][model_name][f"rank_{rank_id}"] = datetime.utcnow(
    )
    # now scan the heartbeats of the requested model_name, the tolerance is 30 seconds, i.e., only when all ranks appear in the heartbeats within 30 seconds, we consider the model is still alive
    up_count = 0
    is_alive = False
    for rank_id in coord_status['models']['heartbeats'][model_name]:
        if (current_time - coord_status['models']['heartbeats'][model_name][rank_id]).total_seconds() < 30:
            up_count += 1
    if up_count == machine_size_mapping[model_name]:
        is_alive = True

    if is_alive:
        # tell global coordinator that this model is alive
        planetml_client.update_model_status(model=model_name, payload={
            "warmness": 1,
            "last_heartbeat": datetime.utcnow()
        })
        coord_status['models']['warmness'][model_name] = 1
    # regarding returned value, if model_name not in instructions, set it to default
    if model_name not in coord_status['models']['instructions']:
        coord_status['models']['instructions'][model_name] = [
            {"message": "continue"}]
    if model_name not in counter_instructions:
        counter_instructions[model_name] = {}
        counter_instructions[model_name][0] = coord_status['models']['instructions'][model_name]
    else:
        if counter not in counter_instructions[model_name]:
            counter_instructions[model_name][counter] = coord_status['models']['instructions'][model_name]
        else:
            pass
    return counter_instructions[model_name][counter]

@lc_app.on_event("shutdown")
def shutdown_event():
    logger.info("dumping results to local db...")


def update_warmnesses():
    current_time = datetime.utcnow()
    logger.info("updating warmnesses...")
    for model_name in coord_status['warm_watch']:
        if model_name in coord_status['models']['warmness']:
            if coord_status['models']["warmness"][model_name] == 0.5:
                continue
        else:
            coord_status['models']['warmness'][model_name] = 0
        if model_name in coord_status['models']['heartbeats']:
            up_count = 0
            for rank_id in coord_status['models']['heartbeats'][model_name]:
                if (current_time - coord_status['models']['heartbeats'][model_name][rank_id]).total_seconds() < 30:
                    up_count += 1
            if up_count == machine_size_mapping[model_name]:
                coord_status['models']['warmness'][model_name] = 1
                planetml_client.update_model_status(model=model_name, payload={
                    "warmness": 1,
                    "last_heartbeat": str(current_time)
                })
            else:
                coord_status['models']['warmness'][model_name] = 0
                planetml_client.update_model_status(model=model_name, payload={
                    "warmness": 0,
                    "last_heartbeat": ""
                })
                # then we need to redispatch the job in the instructions queue
                for instruction in coord_status['models']['instructions'][model_name]:
                    if instruction['message'] == 'run':
                        if instruction['payload']['status'] != 'submitted':
                            planetml_client.update_job_status(
                                job_id=instruction['payload']['id'],
                                status="submitted",
                            )
        else:
            planetml_client.update_model_status(model=model_name, payload={
                "warmness": 0,
                "last_heartbeat": ""
            })
    for model_name in coord_status['minimal_warmness']:
        if coord_status['models']['warmness'][model_name] >= 0.5:
            logger.info(
                f"{model_name} is being warmed up or is warmed, skipping...")

        elif coord_status['models']['warmness'][model_name] < coord_status['minimal_warmness'][model_name]:
            # means we need to start a test job
            logger.info(f"dispatching a warming job for model {model_name}")
            requests.post("https://planetd.shift.ml/jobs",
                          json=example_jobs[model_name])
            coord_status['models']['warmness'][model_name] = 0.5

def fetch_submitted_jobs():
    logger.info("Fetching and dispatching jobs")
    jobs = planetml_client.get_jobs()
    bi_jobs = [x for x in jobs
               if x['source'] == 'dalle'
               and x['status'] == 'submitted'
               and x['type'] == 'general'
               ]
    logger.info("Found {} general jobs".format(len(bi_jobs)))
    if len(bi_jobs) > 0:
        bi_coordinator = BatchInferenceCoordinator(
            "batch_inference",
            coord_status=coord_status,
        )
    for each in bi_jobs:
        if each['id'] in coord_status['known_jobs']:
            each, is_interactive = known_jobs_data[each['id']]
        else:
            try:
                each, is_interactive = preprocess_job(each)
                known_jobs_data[each['id']] = (each, is_interactive)
                coord_status['known_jobs'].append(each['id'])
            except Exception as e:
                error = traceback.format_exc()
                logger.error(error)
                planetml_client.update_job_status(
                    job_id=each['id'],
                    processed_by="",
                    status="failed",
                    source=each['source'],
                    type=each['type'],
                    returned_payload={"message": str(e)}
                )
                return
        if each['payload'][0]['model'] not in machine_size_mapping:
            logger.warning(
                f"model {each['payload'][0]['model']} not in machine_size_mapping, skipping...")
            continue
        # here if it is a file, i.e., url is provided, we regard it as a batch inference job
        # otherwise, it is an interactive job - we will dispatch it to a live coordinator
        # if no live coordinator is available, we will create a new one
        try:
            if not is_interactive or not each['payload'][0]['model'] in coord_status['models']['warmness']:
                # it's not an interactive job, or the model is not warm,
                # dispatch it to a cluster
                job_payload[each['id']] = each['payload']
                dispatch_result = bi_coordinator.dispatch(each)
                if dispatch_result is not None:
                    coord_status['inqueue_jobs'][dispatch_result['cluster']].append(
                        each['id'])
                    if each['id'] in coord_status['known_jobs']:
                        coord_status['known_jobs'].remove(each['id'])
                        del known_jobs_data[each['id']]
            else:
                # for interactive job
                # first check warmness
                # put it into instructions list
                if coord_status['models']['warmness'][each['payload'][0]['model']] >= 1:
                    logger.info(
                        f"model {each['payload'][0]['model']} is warm, dispatching to live worker")
                    if each['payload'][0]['model'] not in coord_status['models']['instructions']:
                        coord_status['models']['instructions'][each['payload'][0]['model']] = [
                            {"message": "continue"}]
                    coord_status['models']['instructions'][each['payload'][0]['model']].append({
                        "message": "run",
                        "payload": each
                    })
                    if each['id'] in coord_status['known_jobs']:
                        coord_status['known_jobs'].remove(each['id'])
                        del known_jobs_data[each['id']]
                else:
                    # this model is warm in the past, but not now
                    job_payload[each['id']] = each['payload']
                    dispatch_result = bi_coordinator.dispatch(each)
                    if dispatch_result is not None:
                        coord_status['inqueue_jobs'][dispatch_result['cluster']].append(
                            each['id'])
                        if each['id'] in coord_status['known_jobs']:
                            coord_status['known_jobs'].remove(each['id'])
                            del known_jobs_data[each['id']]
        except Exception as e:
            error = traceback.format_exc()
            logger.error(error)
            planetml_client.update_job_status(
                job_id=each['id'],
                processed_by="",
                status="failed",
                source=each['source'],
                type=each['type'],
                returned_payload={"message": error}
            )
            del coord_status['known_jobs'][each['id']]
            raise e.with_traceback()


@lc_app.on_event("startup")
@repeat_every(seconds=10)  # fetch jobs every $ seconds， but check submit lock
def periodical():
    try:
        update_warmnesses()
        fetch_submitted_jobs()
    except Exception as e:
        error = traceback.format_exc()
        logger.error(error)
    failed_job = planetml_client.check_job_timeout()
    # update coord_status['inqueue_jobs']
    for cluster in coord_status['inqueue_jobs']:
        for job_id in coord_status['inqueue_jobs'][cluster]:
            if job_id in failed_job:
                coord_status['inqueue_jobs'][cluster].remove(job_id)
    update_instructions()
