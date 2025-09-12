from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy import Enum as saEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from api.core.database import Base
from api.src.enums import EnumUserRoles


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(
        saEnum(EnumUserRoles, name="enumuserroles"), unique=False, nullable=False
    )
    is_active = Column(Boolean, nullable=False, default=True)
    profile_picture_id = Column(Integer, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    properties = relationship(
        "Property",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    leases = relationship(
        "Lease",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    profile_picture = relationship(
        "ProfilePicture",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
