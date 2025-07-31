from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from api.core.database import Base


class Unit(Base):
    __tablename__ = "units"
    __table_args__ = (
        UniqueConstraint("property_id", "name", name="uq_unit_name_per_property"),
    )

    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)  # e.g., "Room A", "Apt 2"
    description = Column(Text, nullable=True)
    monthly_rent = Column(Float, nullable=False)

    property = relationship("Property", back_populates="units")
    leases = relationship("Lease", back_populates="unit", cascade="all, delete-orphan")
