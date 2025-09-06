from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from api.core.database import Base


class Unit(Base):
    __tablename__ = "units"
    __table_args__ = (
        UniqueConstraint("property_id", "name", name="uq_unit_name_per_property"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)  # e.g., "Room A", "Apt 2"
    description = Column(Text, nullable=True)
    monthly_rent = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    property = relationship("Property", back_populates="units")
    leases = relationship("Lease", back_populates="unit", cascade="all, delete-orphan")
