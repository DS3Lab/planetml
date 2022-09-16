from copy import deepcopy
import boto3
import rollbar
import requests
from uuid import uuid4
from typing import List
import os
from pydantic import BaseSettings
from fastapi.datastructures import UploadFile
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, File, UploadFile
from sqlmodel import create_engine, SQLModel, Session, select
from rollbar.contrib.fastapi import add_to as rollbar_add_to

from schemas.job import Job
from schemas.resource import Site, SiteStat
from schemas.model import ModelStatus
from constants import SPLIT_LAMBDA_URL

class Settings(BaseSettings):
    db_database: str
    db_username: str
    db_host: str
    db_password: str
    rollbar_key: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


rollbar.init(Settings().rollbar_key)

app = FastAPI(title="TOMA API", description="Together Open Inference Program", version="0.1.0")
rollbar_add_to(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = None
s3 = boto3.client("s3")

@app.on_event("startup")
def on_startup():
    global engine
    settings = Settings()
    if engine is None:
        engine = create_engine(
            f"postgresql://{settings.db_username}:{settings.db_password}@{settings.db_host}/{settings.db_database}")

@app.post("/sites", response_model=Site)
def add_site(site: Site):
    """
    Adding a new computation site to the database
    """
    with Session(engine) as session:
        session.add(site)
        session.commit()
        session.refresh(site)
        return site

@app.post("/site_stats", response_model=SiteStat)
def add_resource(stat: SiteStat):
    """
    Adding Resource Stats to the database
    * `id` and `created_at` are optional (will be generated if not provided)
    * `created_at` will be generated as utcnow()
    """
    with Session(engine) as session:
        session.add(stat)
        session.commit()
        session.refresh(stat)
        return stat

@app.post("/jobs", response_model=Job)
def add_job(job: Job):
    """
    Adding a new job to the database
    * If jobs is too large, then splits it into multiple jobs, the old job will be marked as type=shadow. Threshold is fixed now to be 1000 (rows), or 10 MB (if file is provided, not implemented yet)
    * The slice should be determined dynamically, but now it is set to be 100
    """
    with Session(engine) as session:
        # if job payload contains url, and this url is managed by us
        # dispatch a lambda function, which checks if the job is too large and needs to be split
        if 'url' in job.payload:
            if job.payload['url'].startswith('https://planetd.shift.ml'):
                # later we will also check it here
                res = requests.post(SPLIT_LAMBDA_URL, json={
                    "file_id": job.payload['url'].rsplit('/')[-1],
                    "bucket": "toma-all"
                })
                response = res.json()
                if response['status_code'] == 100:
                    # no split happened
                    session.add(job)
                    session.commit()
                    session.refresh(job)
                elif response['status_code'] == 200:
                    # at this time, sub jobs will be added to the database
                    file_ids = response['file_ids']
                    job.subjobs = []
                    for fid in file_ids:
                        sub_job:Job = Job(
                            payload = {
                                "url": f"https://planetd.shift.ml/files/{fid}",
                            },
                            type = job.type,
                            status = job.status,
                            processed_by = job.processed_by,
                            source= job.source,
                        )
                        job.subjobs.append(str(sub_job.id))
                        session.add(sub_job)
                    job.type = "shadow"
                    session.add(job)
                    session.commit()
                    session.refresh(job)
            else:
                session.add(job)
                session.commit()
                session.refresh(job)
        else:
            session.add(job)
            session.commit()
            session.refresh(job)
    return job

@app.get("/model_statuses")
def get_model_status():
    """
    Get all model statuses
    """
    with Session(engine) as session:
        statement = select(ModelStatus)
        model_statuses = session.exec(statement).all()
        return model_statuses

@app.patch("/model_statuses/{model_name}")
def patch_model_status(model_name:str, model_status:ModelStatus):
    with Session(engine) as session:
        to_update_model_status = select(ModelStatus).where(ModelStatus.name == model_name)
        to_update_model_status = session.exec(to_update_model_status).first()
        if to_update_model_status is None:
            to_update_model_status = model_status
            session.add(to_update_model_status)
            session.commit()
            session.refresh(to_update_model_status)
        else:
            to_update_model_status.warmness = model_status.warmness
            to_update_model_status.expected_runtime = model_status.expected_runtime
            if model_status.last_heartbeat!="":
                to_update_model_status.last_heartbeat = model_status.last_heartbeat
            session.add(to_update_model_status)
            session.commit()
            session.refresh(to_update_model_status)
    return to_update_model_status
    
@app.get("/sites")
def get_sites():
    """
    Get all sites
    """
    with Session(engine) as session:
        sites = session.query(Site).all()
        results = []
        for site in sites:
            # this should be done automatically by sqlalchemy, maybe in the future
            statement = select(SiteStat).where(
                SiteStat.site_identifier == site.identifier).order_by(SiteStat.created_at.desc())
            stats = session.execute(statement).first()
            site_dict = site.dict()
            site_dict["stats"] = stats
            results.append(site_dict)
        return results

@app.get("/site_stats", response_model=List[SiteStat])
def get_site_stats():
    """
    Get all site stats
    This only returns the essential information, including: 
     id, created_at, site_identifier, note, scheduler_type, and 
     total_gpus, total_tflops, avail_gpus, avail_tflops
    """
    with Session(engine) as session:
        return session.exec(select(
            SiteStat.id,
            SiteStat.created_at,
            SiteStat.total_tflops,
            SiteStat.avail_tflops,
            SiteStat.total_gpus,
            SiteStat.avail_gpus,
            SiteStat.scheduler_type,
            SiteStat.note,
            SiteStat.site_identifier,
        ).order_by(SiteStat.created_at.desc()).limit(150)).all()

@app.get("/site_stats_full", response_model=List[SiteStat])
def get_site_stats():
    """
    Get all site stats
    This returns full information, including resources
    """
    with Session(engine) as session:
        return session.query(SiteStat).order_by(SiteStat.created_at.desc()).limit(150).all()

@app.get("/jobs", response_model=List[Job])
def get_jobs():
    """
    Get all jobs
    """
    with Session(engine) as session:
        return session.query(Job).all()

@app.get("/job/{id}", response_model=Job)
def get_job(id):
    """
    Get a job by id
    """
    with Session(engine) as session:
        job = session.get(Job, id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")
        return job

@app.get("/jobs/submitted", response_model=List[Job])
def get_unfinished_jobs(limit=10):
    """
    Get only submitted jobs (for local coordinators to dispatch)
    * limit: the number of jobs to return
    * Each pulled job will be marked as "pulled" in its status, meaning that it has arrived at the local coordinator
    * The local coordinator should then mark the job as "running" when it starts to process the job
    """
    with Session(engine) as session:
        results = session.query(Job).where(Job.status=='submitted').limit(limit).all()
        returned_results = deepcopy(results)
        
        if len(results) > 0:
            for job in results:
                job.status = 'pulled'
                session.add(job)
            session.commit()
        else:
            returned_results = []
        return returned_results


@app.patch("/jobs/{id}")
def update_job(id: str, job: Job):
    """
    Update a job
    """
    with Session(engine) as session:
        job_to_update = select(Job).where(Job.id == job.id)
        job_to_update = session.exec(job_to_update).first()
        if job_to_update is None:
            return {"message": "job not found"}
        if job_to_update.status != 'finished':
            if job_to_update is None:
                return {"message": "Job not found"}
            if job.processed_by != "":
                job_to_update.processed_by = job.processed_by
            if job.status != "":
                job_to_update.status = job.status
            if job.returned_payload != {}:
                job_to_update.returned_payload = job.returned_payload
            session.add(job_to_update)
            session.commit()
            session.refresh(job_to_update)
            return job_to_update
        else:
            return {"message": "Job is already finished, and in an immutable state"}

@app.get("/files/{filename}")
def access_s3(filename: str):
    try:
        result = s3.get_object(Bucket="toma-all", Key=filename)
        return StreamingResponse(content=result["Body"].iter_chunks())
    except Exception as e:
        return {"status":"error","message": str(e)}

@app.post("/file")
def upload_file_to_s3(file: UploadFile = File(...)):
    with file.file as bytestream:
        try:
            extension = os.path.splitext(file.filename)[1][1:]
            if len(extension) == 0:
                extension = 'json'
            filename = f"{str(uuid4())}.{extension}"
            s3.upload_fileobj(bytestream, "toma-all", filename)
        except Exception as e:
            return {"status":"error","message": str(e)}
    return {"message":"ok", "filename": f"https://planetd.shift.ml/files/{filename}"}

if __name__ == "__main__":
    settings = Settings()
    engine = create_engine(
        f"postgresql://{settings.db_username}:{settings.db_password}@{settings.db_host}/{settings.db_database}")
    SQLModel.metadata.create_all(engine)
