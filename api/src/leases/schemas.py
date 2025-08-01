from pydantic import BaseModel
from datetime import date
from typing import Optional


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

    model_config = {"from_attributes": True}
