import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CohorteBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    carrera_id: uuid.UUID


class CohorteCreate(CohorteBase):
    model_config = ConfigDict(extra="forbid")


class CohorteUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    carrera_id: Optional[uuid.UUID] = None
    is_active: Optional[bool] = None


class CohorteRead(CohorteBase):
    id: uuid.UUID
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
