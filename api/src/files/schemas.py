from datetime import datetime

from pydantic import BaseModel


class FileBase(BaseModel):
    """Base schema for file operations."""

    filename: str
    mimetype: str
    size: int


class FileCreate(FileBase):
    """Schema for creating a file."""

    data: bytes


class FileResponse(FileBase):
    """Schema for file responses."""

    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class FileDownload(BaseModel):
    """Schema for file download response."""

    filename: str
    mimetype: str
    data: bytes
    size: int
