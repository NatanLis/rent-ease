from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from api.src.enums import EnumUserRoles


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str
    role: EnumUserRoles


class TenantCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    email: EmailStr | None = None
    is_active: bool | None = None
    location: str | None = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role: EnumUserRoles
    is_active: bool
    created_at: str
    updated_at: str | None = None
    profile_picture_id: int | None = None
    avatar_url: str | None = None
    status: str | None = None
    location: str | None = None

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def convert_datetime_to_string(cls, value):
        if isinstance(value, datetime):
            return value.isoformat()
        return value


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginData(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    user: UserResponse
    token: Token
