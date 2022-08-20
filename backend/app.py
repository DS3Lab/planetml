import datetime
from schemas.resource import ResourceStats
from fastapi import FastAPI
from pydantic import BaseSettings
from sqlmodel import create_engine, SQLModel, Session
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

@app.post("/resource_stats", response_model=ResourceStats)
def add_resource(resource: ResourceStats):
    """
    Adding Resource Stats to the database
    * `id` and `created_at` are optional (will be generated if not provided)
    * `created_at` will be generated as utcnow()
    """
    with Session(engine) as session:
        if resource.created_at is None:
            resource.created_at = datetime.datetime.utcnow()
        session.add(resource)
        session.commit()
        session.refresh(resource)
        return resource

if __name__=="__main__":
    settings = Settings()
    engine = create_engine(f"postgresql://{settings.db_username}:{settings.db_password}@{settings.db_host}/{settings.db_database}")
    SQLModel.metadata.create_all(engine)