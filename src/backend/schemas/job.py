import enum
import datetime
import uuid as uuid_pkg
from sqlalchemy import Column
from typing import Optional, Dict, List, Union
from sqlmodel import Field, SQLModel,JSON
from sqlalchemy.types import Enum, DateTime
from sqlalchemy.ext.mutable import MutableDict

class JobStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    QUEUED = "queued"
    RUNNING = "running"
    FINISHED = "finished"
    FAILED = "failed"
    PULLED = "pulled"

class JobType(str, enum.Enum):
    GENERAL = 'general'
    INFERENCE = 'inference'
    CLASSIFICATION = 'classification'
    SHADOW = 'shadow' # shadow task - tasks that have childrens

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
    payload: Union[Dict, List] = Field(default={}, sa_column=Column(JSON))
    returned_payload: Union[Dict, List] = Field(MutableDict.as_mutable(JSON), sa_column=Column(JSON))

    status: JobStatus = Field(sa_column=Column(Enum(JobStatus)))
    source: JobSource = Field(sa_column=Column(Enum(JobSource)))
    created_at: Optional[datetime.datetime] = Field(sa_column=Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow))

    processed_by: Optional[str]
    subjobs: Optional[List[str]]

    class Config:
        arbitrary_types_allowed = True