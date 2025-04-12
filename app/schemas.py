from pydantic import BaseModel
from typing import Optional

# --- USER ---

# Pydantic model for the User
class UserSchema(BaseModel):
    name: str
    email: str
    nickname: Optional[str] = None

# Model for Token response (contains access token and token type)
class Token(BaseModel):
    access_token: str
    token_type: str

# Model for token data (used to extract user information from the token)
class TokenData(BaseModel):
    email: str
    # You can add more fields if needed (e.g. id, name, etc.)

# --- PROPERTY ---

class PropertyBase(BaseModel):
    title: str
    description: Optional[str] = None
    address: str
    price: float

class PropertyCreate(PropertyBase):
    pass

class Property(PropertyBase):
    id: int

    class Config:
        orm_mode = True

# --- ALERT ---

class AlertBase(BaseModel):
    message: str
    is_resolved: bool = False

class AlertCreate(AlertBase):
    pass

class Alert(AlertBase):
    id: int

    class Config:
        orm_mode = True

# --- INVOICE ---

class InvoiceBase(BaseModel):
    amount: float
    description: Optional[str] = None
    is_paid: bool = False

class InvoiceCreate(InvoiceBase):
    pass

class Invoice(InvoiceBase):
    id: int

    class Config:
        orm_mode = True

# --- MESSAGE ---

class MessageBase(BaseModel):
    sender: str
    receiver: str
    content: str

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int

    class Config:
        orm_mode = True

# --- PAYMENT ---

class PaymentBase(BaseModel):
    invoice_id: int
    amount: float

class PaymentCreate(PaymentBase):
    pass

class Payment(PaymentBase):
    id: int
    status: str  # e.g. "pending", "completed"

    class Config:
        orm_mode = True
