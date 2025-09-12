from typing import Optional

from pydantic import BaseModel, ConfigDict


class UnitBase(BaseModel):
    property_id: int
    name: str
    description: Optional[str] = None
    monthly_rent: float


class UnitCreate(UnitBase):
    pass


class UnitUpdate(UnitBase):
    property_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    monthly_rent: Optional[float] = None


class UnitResponse(UnitBase):
    id: int
    property_title: Optional[str] = None
    property_address: Optional[str] = None
    active_leases: int = 0
    status: str = "available"

    model_config = ConfigDict(from_attributes=True)
