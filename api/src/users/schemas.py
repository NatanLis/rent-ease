from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from api.src.enums import EnumUserRoles


class UserBase(BaseModel):
    """Base user schema."""

    first_name: str
    last_name: str
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
    is_active: bool
    created_at: str
    updated_at: str | None = None
    profile_picture_id: int | None = None
    avatar_url: str | None = None  # URL to profile picture
    status: str | None = None  # "active" if has active lease, "inactive" otherwise
    location: str | None = None  # Current address from active lease property

    @field_validator('created_at', 'updated_at', mode='before')
    @classmethod
    def convert_datetime_to_string(cls, v):
        """Convert datetime objects to ISO format strings."""
        if isinstance(v, datetime):
            return v.isoformat()
        return v


class Token(BaseModel):
    """Token schema."""

    access_token: str
    token_type: str = "bearer"


class LoginData(BaseModel):
    """Login data schema."""

    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response schema."""
    user: UserResponse
    token: Token
