import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CarreraBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    code: str = Field(min_length=1, max_length=50)


class CarreraCreate(CarreraBase):
    model_config = ConfigDict(extra="forbid")


class CarreraUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    code: Optional[str] = Field(default=None, min_length=1, max_length=50)
    is_active: Optional[bool] = None


class CarreraRead(CarreraBase):
    id: uuid.UUID
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
