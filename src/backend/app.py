import boto3
import boto3
from schemas.resource import Site, SiteStat
from schemas.job import Job
from typing import List
from fastapi import FastAPI
from pydantic import BaseSettings
from sqlmodel import create_engine, SQLModel, Session, select
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.responses import StreamingResponse
import rollbar
from rollbar.contrib.fastapi import add_to as rollbar_add_to
from fastapi import FastAPI, HTTPException
from fastapi import FastAPI, HTTPException

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

app = FastAPI(title="TOMA API",
              description="Together Open Inference Program", version="0.1.0")
rollbar_add_to(app)


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*']
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
    """
    with Session(engine) as session:
        session.add(job)
        session.commit()
        session.refresh(job)
        return job

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
    This returns full information
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

@app.get("/jobs/unfinished", response_model=List[Job])
def get_unfinished_jobs():
    """
    Get all unfinished jobs
    # TODO: add a filter to the query
    """
    with Session(engine) as session:
        return session.query(Job).all()
@app.get("/jobs/unfinished", response_model=List[Job])
def get_unfinished_jobs():
    """
    Get all unfinished jobs
    # TODO: add a filter to the query
    """
    with Session(engine) as session:
        return session.query(Job).all()
@app.get("/jobs/unfinished", response_model=List[Job])
def get_unfinished_jobs():
    """
    Get all unfinished jobs
    # TODO: add a filter to the query
    """
    with Session(engine) as session:
        return session.query(Job).all()
@app.get("/jobs/unfinished", response_model=List[Job])
def get_unfinished_jobs():
    """
    Get all unfinished jobs
    # TODO: add a filter to the query
    """
    with Session(engine) as session:
        return session.query(Job).all()

@app.patch("/jobs/{id}", response_model=Job)
def update_job(id: str, job: Job):
    """
    Update a job
    """
    with Session(engine) as session:
        job_to_update = select(Job).where(Job.id == job.id)
        job_to_update = session.exec(job_to_update).one()
        if job_to_update is None:
            return {"message": "Job not found"}
        job_to_update.processed_by = job.processed_by
        job_to_update.status = job.status
        job_to_update.returned_payload = job.returned_payload
        job_to_update.returned_payload = job.returned_payload
        session.add(job_to_update)
        session.commit()
        session.refresh(job_to_update)
        return job_to_update

@app.get("/files/{filename}")
def access_s3(filename: str):
    try:
        result = s3.get_object(Bucket="toma-all", Key=filename)
        return StreamingResponse(content=result["Body"].iter_chunks())
    except Exception as e:
        if hasattr(e, "message"):
            raise HTTPException(
                status_code=e.message["response"]["Error"]["Code"],
                detail=e.message["response"]["Error"]["Message"],
            )
        else:
            raise HTTPException(status_code=500, detail=str(e))
@app.get("/files/{filename}")
def access_s3(filename: str):
    try:
        result = s3.get_object(Bucket="toma-all", Key=filename)
        return StreamingResponse(content=result["Body"].iter_chunks())
    except Exception as e:
        if hasattr(e, "message"):
            raise HTTPException(
                status_code=e.message["response"]["Error"]["Code"],
                detail=e.message["response"]["Error"]["Message"],
            )
        else:
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    settings = Settings()
    engine = create_engine(
        f"postgresql://{settings.db_username}:{settings.db_password}@{settings.db_host}/{settings.db_database}")
    SQLModel.metadata.create_all(engine)