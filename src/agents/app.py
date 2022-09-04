from fastapi import FastAPI, Request
from fastapi_utils.tasks import repeat_every
from loguru import logger
from pydantic import BaseSettings

lc_app = FastAPI(debug=True)
watched_jobs = {}
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

# the behavior of this script should be controlled by a config file - which agents should be loaded and supervised, etc. - later later...
import sys
sys.path.append('./')
from src.agents.instances.batch_inference.batch_inference_agent import BatchInferenceCoordinator
from src.agents.utils.planetml import PlanetML
from src.agents.utils.pprint import print_table
from src.agents.clients.LSFClient import LSFClient

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
    print(res.json())
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
        lsf_client._connect()
        bi_coordinator = BatchInferenceCoordinator("batch_inference", lsf_client)
        logger.info("Fetching and dispatching jobs")
        jobs = planetml_client.get_jobs()
        bi_jobs = [x for x in jobs if x['source']=='dalle' and x['status']=='submitted']
        logger.info("Found {} jobs batch inference".format(len(bi_jobs)))
        for each in bi_jobs:
            watched_jobs[each['id']] = each
            bi_coordinator.dispatch(each)


    except Exception as e:
        logger.error(e)
