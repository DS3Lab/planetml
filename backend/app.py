from schemas.resource import Site,SiteStat
from schemas.job import Job
from typing import List
from fastapi import FastAPI
from pydantic import BaseSettings
from sqlmodel import create_engine, SQLModel, Session, select
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="PlanetML API", description="PlanetML API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*']
)

engine = None

class Settings(BaseSettings):
    db_database: str
    db_username: str
    db_host: str
    db_password: str
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

@app.on_event("startup")
def on_startup():
    
    global engine
    settings = Settings()
    engine = create_engine(f"postgresql://{settings.db_username}:{settings.db_password}@{settings.db_host}/{settings.db_database}")

@app.get("/")
async def root():
    return {"message": "Hello World"}

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

@app.get("/sites", response_model=List[Site])
def get_sites():
    """
    Get all sites
    """
    with Session(engine) as session:
        return session.query(Site).all()

@app.get("/site_stats", response_model=List[SiteStat])
def get_site_stats():
    """
    Get all site stats
    """
    with Session(engine) as session:
        return session.query(SiteStat).all()

if __name__=="__main__":
    settings = Settings()
    engine = create_engine(f"postgresql://{settings.db_username}:{settings.db_password}@{settings.db_host}/{settings.db_database}")
    SQLModel.metadata.create_all(engine)