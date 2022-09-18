import sys
from tempfile import TemporaryFile
from loguru import logger
from typing import Optional
from datetime import datetime
from pydantic import BaseSettings
from fastapi import FastAPI, Request
from fastapi_utils.tasks import repeat_every

sys.path.append('./')
from src.agents.utils.planetml import PlanetML

class Settings(BaseSettings):
    euler_lsf_host: Optional[str]
    euler_lsf_username: Optional[str]
    euler_lsf_password: Optional[str]
    euler_lsf_wd: Optional[str]
    euler_lsf_init: Optional[str]

    class Config:
        env_file = 'src/agents/.env'
        env_file_encoding = 'utf-8'

dataperf_app=FastAPI(debug=True, docs_url='/dataperf/docs', openapi_url='/dataperf/api/v1/openapi.json')
planetml_client = PlanetML()

def fetch_submitted_jobs():
    try:
        logger.info("Fetching submitted jobs")
        jobs = planetml_client.get_jobs()
        dp_jobs = [x for x in jobs 
            if x['status']=='submitted'
            and x['source'] == 'dataperf'
        ]
        logger.info("Found {} submitted jobs".format(len(dp_jobs)))
    except Exception as e:
        logger.error(e)
        return

@dataperf_app.post("/dataperf/update_status/{id}")
async def update_status(id, req: Request):
    request_json = await req.json()
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

@dataperf_app.on_event("startup")
@repeat_every(seconds=10)  # fetch jobs every $ seconds， but check submit lock
def periodical():
    fetch_submitted_jobs()
