from sqlalchemy import Column
from sqlalchemy import Enum as saEnum
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship

from api.core.database import Base
from api.src.enums import EnumUserRoles


class User(Base):
    """User model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(saEnum(EnumUserRoles, name="enumuserroles"), unique=False, nullable=False)

    properties = relationship(
        "Property",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    leases = relationship("Lease", back_populates="tenant", cascade="all, delete-orphan")

    leases = relationship(
        "Lease",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
