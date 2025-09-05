from typing import Optional

from pydantic import BaseModel, ConfigDict


class UnitBase(BaseModel):
    property_id: int
    name: str
    description: Optional[str] = None
    monthly_rent: float


class UnitCreate(UnitBase):
    """Unit response schema."""


class UnitUpdate(UnitBase):
    """Schema for updating an existing property.

    All fields are optional since updates might be partial.
    """

    property_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    monthly_rent: Optional[float] = None


class UnitResponse(UnitBase):
    """Schema for unit responses.

    Includes all base fields plus the id.
    """

    id: int

    model_config = ConfigDict(from_attributes=True)
