from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PropertyBase(BaseModel):
    title: str
    description: Optional[str] = None
    address: str
    price: float
    owner_id: Optional[int] = None


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(PropertyBase):
    title: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, min_length=1, max_length=100)
    address: str | None = None
    price: int | None = None


class PropertyResponse(PropertyBase):
    id: int
    units_count: int = 0
    active_leases: int = 0
    model_config = ConfigDict(from_attributes=True)
