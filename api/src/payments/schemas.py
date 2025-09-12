from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class PaymentFrequency(str, Enum):
    """Payment frequency options."""

    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class PaymentBase(BaseModel):
    """Base payment schema with common fields."""

    document_type: str = Field(
        ..., description="Type of document (Rent Invoice, Security Deposit, etc.)"
    )
    gross_value: float = Field(..., gt=0, description="Payment amount in PLN")
    due_date: date = Field(..., description="Payment due date")
    receiver: str = Field(..., description="Name or email of payment receiver")
    description: Optional[str] = Field(
        None, description="Optional payment description"
    )
    lease_id: Optional[int] = Field(None, description="Associated lease ID")
    invoice_file_id: Optional[int] = Field(None, description="Invoice file ID")


class PaymentCreate(PaymentBase):
    """Schema for creating a new payment."""

    pass


class RecurringPaymentCreate(BaseModel):
    """Schema for creating recurring payments for a lease."""

    lease_id: int = Field(..., description="Lease ID for which to create payments")
    document_type: str = Field(
        ..., description="Type of document (Rent Invoice, Security Deposit, etc.)"
    )
    amount: float = Field(..., gt=0, description="Total payment amount")
    frequency: PaymentFrequency = Field(..., description="Payment frequency")
    due_day: int = Field(
        ..., ge=1, le=31, description="Day of month when payment is due"
    )
    description: Optional[str] = Field(
        None, description="Optional payment description"
    )

    @field_validator("due_day")
    @classmethod
    def validate_due_day(cls, v):
        if not 1 <= v <= 31:
            raise ValueError("Due day must be between 1 and 31")
        return v


class RecurringPaymentResponse(BaseModel):
    """Response schema for recurring payment creation."""

    lease_id: int
    payments_created: int
    total_amount: float
    frequency: PaymentFrequency
    due_day: int
    payments: list[int]  # List of created payment IDs


class PaymentUpdate(BaseModel):
    """Schema for updating payment information."""

    document_type: Optional[str] = None
    gross_value: Optional[float] = Field(None, gt=0)
    due_date: Optional[date] = None
    receiver: Optional[str] = None
    description: Optional[str] = None
    lease_id: Optional[int] = None
    is_paid: Optional[bool] = None


class PaymentStatusUpdate(BaseModel):
    """Schema for updating payment status only."""

    is_paid: bool = Field(..., description="Payment status")


class PaymentInvoiceUpdate(BaseModel):
    """Schema for attaching invoice to payment."""

    invoice_file_id: int = Field(..., description="Invoice file ID")


class UserInfo(BaseModel):
    """User information schema."""

    id: int
    email: str
    first_name: str
    last_name: str
    avatar_url: Optional[str] = None

    model_config = {"from_attributes": True}


class PropertyInfo(BaseModel):
    """Property information schema."""

    id: int
    title: str
    address: str

    model_config = {"from_attributes": True}


class UnitInfo(BaseModel):
    """Unit information schema."""

    id: int
    name: str
    monthly_rent: float
    property: PropertyInfo

    model_config = {"from_attributes": True}


class LeaseInfo(BaseModel):
    """Lease information schema for payment responses."""

    id: int
    unit_id: int
    tenant_id: int
    user: UserInfo
    unit: UnitInfo

    model_config = {"from_attributes": True}


class FileInfo(BaseModel):
    """File information schema."""

    id: int
    filename: str
    mimetype: str
    size: int

    model_config = {"from_attributes": True}


class PaymentResponse(PaymentBase):
    """Schema for payment responses."""

    id: int
    is_paid: bool
    status: str  # Computed field: 'Paid', 'Pending', 'Overdue'
    created_at: str
    updated_at: Optional[str] = None
    lease: Optional[LeaseInfo] = None
    invoice_file: Optional[FileInfo] = None

    model_config = {"from_attributes": True}

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def convert_datetime_to_string(cls, value):
        if isinstance(value, datetime):
            return value.isoformat()
        return value


class PaymentListResponse(BaseModel):
    """Schema for paginated payment list responses."""

    payments: list[PaymentResponse]
    total: int
    page: int
    size: int
    pages: int
