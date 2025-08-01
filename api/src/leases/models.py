from sqlalchemy import Column, Integer, Date, Boolean, ForeignKey, UniqueConstraint, DateTime, func
from sqlalchemy.orm import relationship

from api.core.database import Base


class Lease(Base):
    __tablename__ = "leases"
    __table_args__ = (
        UniqueConstraint("unit_id", "tenant_id", "start_date", name="uq_lease_unique"),
    )

    id = Column(Integer, primary_key=True, index=True)
    unit_id = Column(Integer, ForeignKey("units.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)  # null means ongoing
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    unit = relationship("Unit", back_populates="leases")
    tenant = relationship("User", back_populates="leases")
