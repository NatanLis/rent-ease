from pydantic import BaseModel, ConfigDict, EmailStr
from api.src.enums import EnumUserRoles

class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr


class UserCreate(UserBase):
    """User creation schema."""

    password: str
    role: EnumUserRoles


class UserResponse(UserBase):
    """User response schema."""

    model_config = ConfigDict(from_attributes=True)
    id: int
    role: EnumUserRoles
    status: str | None = None  # "active" if has active lease, "inactive" otherwise
    location: str | None = None  # Current address from active lease property


class Token(BaseModel):
    """Token schema."""

    access_token: str
    token_type: str = "bearer"


class LoginData(BaseModel):
    """Login data schema."""

    email: EmailStr
    password: str
