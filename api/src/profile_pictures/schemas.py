from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ProfilePictureBase(BaseModel):
    """Base schema for profile picture."""

    filename: str
    mimetype: str
    size: int


class ProfilePictureCreate(ProfilePictureBase):
    """Schema for creating a profile picture."""

    data: bytes


class ProfilePictureResponse(ProfilePictureBase):
    """Schema for profile picture response."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProfilePictureDownload(BaseModel):
    """Schema for profile picture download."""

    id: int
    filename: str
    mimetype: str
    data: bytes
