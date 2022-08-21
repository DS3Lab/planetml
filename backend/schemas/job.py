import datetime
import enum
import uuid as uuid_pkg
from typing import Optional, Dict
from sqlalchemy import Column
from sqlalchemy.types import Enum, DateTime
from sqlmodel import Field, SQLModel, create_engine,JSON

class JobStatus(str, enum.Enum):
    FINISHED = "finished"
    QUEUED = "queued"
    FAILED = "failed"

class JobType(str, enum.Enum):
    INFERENCE = 'inference'
    CLASSIFICATION = 'classification'

class JobSource(str, enum.Enum):
    DALLE = 'dalle'
    DATAPERF = 'dataperf'
    SHIFT = 'shift'
    OTHER = 'other'

class Job(SQLModel, table=True):
    id: Optional[uuid_pkg.UUID] = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    type: JobType = Field(sa_column=Column(Enum(JobType)))
    payload: Dict = Field(default={}, sa_column=Column(JSON))
    returned_payload: Dict = Field(default={}, sa_column=Column(JSON))

    status: JobStatus = Field(sa_column=Column(Enum(JobStatus)))
    source: JobSource = Field(sa_column=Column(Enum(JobSource)))
    created_at: Optional[datetime.datetime] = Field(sa_column=Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow))

    processed_by: str
    
    class Config:
        arbitrary_types_allowed = True