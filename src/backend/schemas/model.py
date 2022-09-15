from sqlmodel import SQLModel, Field
from typing import Optional
import uuid as uuid_pkg
import datetime
from sqlalchemy.types import DateTime
from sqlalchemy import Column

class ModelStatus(SQLModel, table=True):
    id: Optional[uuid_pkg.UUID] = Field(
        default_factory=uuid_pkg.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    name: str
    warmness: float
    created_at: Optional[datetime.datetime] = Field(sa_column=Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow))
    expected_runtime: int
    last_heartbeat: Optional[datetime.datetime] = Field(sa_column=Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow))

