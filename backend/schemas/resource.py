import datetime
import enum
import uuid as uuid_pkg
from typing import Optional, Dict
from sqlalchemy import Column
from sqlalchemy.types import Enum, DateTime
from sqlmodel import Field, SQLModel, JSON

class ResourceSite(str, enum.Enum):
    STANFORD = 'stanford.edu'
    ETH = 'ethz.ch'
    OSG = 'osg-htc.org'


class ResourceStats(SQLModel, table=True):
    id: Optional[uuid_pkg.UUID] = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    source: ResourceSite = Field(sa_column=Column(Enum(ResourceSite)))
    
    created_at: Optional[datetime.datetime] = Field(sa_column=Column(DateTime(timezone=True), nullable=False))

    total_perfs: float
    num_gpu: int
    num_cpu: int
    note: str

    class Config:
        arbitrary_types_allowed = True