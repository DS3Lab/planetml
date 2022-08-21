import datetime
import enum
import uuid as uuid_pkg
from typing import Optional
from sqlalchemy import Column
from sqlalchemy.types import Enum, DateTime, String
from sqlmodel import Field, SQLModel, Relationship
from typing import List

class Site(SQLModel, table=True):
    id: Optional[uuid_pkg.UUID] = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    name: str
    identifier: str = Field(sa_column=Column("identifier", String, unique=True))
    created_at: Optional[datetime.datetime] = Field(sa_column=Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow))
    lat: str
    lon: str
    stats: List["SiteStat"] = Relationship(back_populates="site")

    class Config:
        arbitrary_types_allowed = True

class SiteStat(SQLModel, table=True):
    id: Optional[uuid_pkg.UUID] = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    created_at: Optional[datetime.datetime] = Field(sa_column=Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow))
    total_perfs: float
    num_gpu: int
    num_cpu: int
    note: str
    site_identifier: Optional[str] = Field(default=None, foreign_key="site.identifier")
    site: Optional[Site] = Relationship(back_populates="stats")

    class Config:
        arbitrary_types_allowed = True