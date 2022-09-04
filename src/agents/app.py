from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from loguru import logger
lc_app = FastAPI()

# the behavior of this script should be controlled by a config file - which agents should be loaded and supervised, etc. - later later...
import sys
sys.path.append('./')
from src.agents.instances.batch_inference.batch_inference_agent import BatchInferenceCoordinator
from src.agents.utils.planetml import PlanetML

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
@repeat_every(seconds=5)  # fetch jobs every 5 seconds
def fetch_failed_or_submitted_jobs():
    logger.info("Fetching and dispatching jobs")
    planetml_client = PlanetML()
    jobs = planetml_client.get_jobs()
    print(jobs)