from datetime import date
from typing import Optional

from pydantic import BaseModel


class LeaseBase(BaseModel):
    unit_id: int
    tenant_id: int
    start_date: date
    end_date: Optional[date] = None


class LeaseCreate(LeaseBase):
    """Lease response schema."""


class LeaseUpdate(LeaseBase):
    """Schema for updating an existing lease.

    All fields are optional since updates might be partial.
    """

    unit_id: Optional[int] = None
    tenant_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class LeaseEnd(LeaseBase):
    end_date: date


class UserInfo(BaseModel):
    """User information for lease response."""
    id: int
    email: str
    first_name: str
    last_name: str
    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}


class PropertyInfo(BaseModel):
    """Property information for lease response."""
    id: int
    title: str
    address: str

    model_config = {"from_attributes": True}


class UnitInfo(BaseModel):
    """Unit information for lease response."""
    id: int
    name: str
    monthly_rent: float
    property: PropertyInfo

    model_config = {"from_attributes": True}


class LeaseResponse(LeaseBase):
    """Schema for returning lease information in API responses.

    Inherits from LeaseBase and includes additional fields such as id
    """

    id: int
    unit_id: int
    tenant_id: int
    start_date: date
    end_date: Optional[date]
    is_active: bool
    
    # Related data from joins
    user: Optional[UserInfo] = None
    unit: Optional[UnitInfo] = None

    model_config = {"from_attributes": True}
