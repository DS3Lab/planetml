# the behavior of this script should be controlled by a config file - which agents should be loaded and supervised, etc. - later later...

from fastapi import FastAPI, Request
from fastapi_utils.tasks import repeat_every
from loguru import logger
from pydantic import BaseSettings
import sys
sys.path.append('./')
from src.agents.instances.batch_inference.batch_inference_agent import BatchInferenceCoordinator
from src.agents.utils.planetml import PlanetML
from src.agents.utils.pprint import print_table
from src.agents.clients.LSFClient import LSFClient

class Settings(BaseSettings):
    euler_lsf_host: str
    euler_lsf_username: str
    euler_lsf_password: str
    euler_lsf_wd: str
    euler_lsf_init: str

    class Config:
        env_file = 'src/agents/.env'
        env_file_encoding = 'utf-8'

lc_app = FastAPI(debug=True, docs_url="/eth/docs", openapi_url="/eth/api/v1/openapi.json")

watched_jobs = {}
settings = Settings()

planetml_client = PlanetML()

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
        watched_jobs[job_id] = [await req.json()]
    else:
        watched_jobs[job_id].append(await req.json())
    return {"prime_ip":watched_jobs[job_id][0], "rank":len(watched_jobs[job_id])-1}

@lc_app.post("/eth/update_status/{id}")
async def update_status(id, req: Request):
    request_json = await req.json()
    print(request_json)
    if request_json['returned_payload']:
        res = planetml_client.update_job_status(
            id,
            status=request_json['status'],
            returned_payload = request_json['returned_payload'],
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
    return {"message": "ok"}

@lc_app.on_event("startup")
@repeat_every(seconds=60)  # fetch jobs every $ seconds
def fetch_failed_or_submitted_jobs():
    try:
        lsf_client = LSFClient(
            host=settings.euler_lsf_host,
            username=settings.euler_lsf_username,
            password=settings.euler_lsf_password,
            wd=settings.euler_lsf_wd,
            init=settings.euler_lsf_init,
        )
        logger.info("Fetching and dispatching jobs")
        jobs = planetml_client.get_jobs()
        bi_jobs = [x for x in jobs if x['source']=='dalle' and x['status']=='submitted']

        logger.info("Found {} jobs batch inference".format(len(bi_jobs)))
        
        if len(bi_jobs) > 0:
            lsf_client._connect()
            bi_coordinator = BatchInferenceCoordinator("batch_inference", lsf_client)
        for each in bi_jobs:
            bi_coordinator.dispatch(each)

    except Exception as e:
        logger.error(e)

if __name__=='__main__':
    import requests
    requests.post("http://coordinator.shift.ml/eth/rank/1", json={"ip":"xxx", "rank": 0})