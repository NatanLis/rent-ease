from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class PropertyBase(BaseModel):
    title: str
    description: Optional[str] = None
    address: str
    price: float
    owner_id: Optional[int] = None


class PropertyCreate(PropertyBase):
    """Property response schema."""


class PropertyUpdate(PropertyBase):
    """Schema for updating an existing property.

    All fields are optional since updates might be partial.
    """

    title: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, min_length=1, max_length=100)
    address: str | None = None
    price: int | None = None


class PropertyResponse(PropertyBase):
    """Schema for property responses.

    Includes all base fields plus the id.
    """

    model_config = ConfigDict(from_attributes=True)
    id: int
    owner_id: int
