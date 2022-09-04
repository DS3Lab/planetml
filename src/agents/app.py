from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from loguru import logger
lc_app = FastAPI()

# the behavior of this script should be controlled by a config file - which agents should be loaded and supervised, etc. - later later...
import sys
sys.path.append('./')
from src.agents.instances.batch_inference.batch_inference_agent import BatchInferenceCoordinator
from src.agents.utils.planetml import PlanetML


bi_coordinator = BatchInferenceCoordinator("batch_inference")
planetml_client = PlanetML()

@lc_app.get("/heartbeat/:id")
async def root():
    return {"message": "ok"}

@lc_app.get("/health")
async def health():
    return {"message": "ok"}

@lc_app.post("/node_join")
async def node_join():
    return {"message": "ok"}

@lc_app.on_event("startup")
@repeat_every(seconds=60)  # fetch jobs every $ seconds
def fetch_failed_or_submitted_jobs():
    logger.info("Fetching and dispatching jobs")
    jobs = planetml_client.get_jobs()
    bi_jobs = [x for x in jobs if x['source']=='dalle']
    for each in bi_jobs:
        bi_coordinator.dispatch(each)