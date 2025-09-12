from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from api.core.database import Base


class Payment(Base):
    """Payment model representing payment records in the system."""

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Basic payment information
    document_type = Column(
        String, nullable=False
    )  # 'Rent Invoice', 'Security Deposit', 'Maintenance Fee', 'Other'
    gross_value = Column(Float, nullable=False)
    due_date = Column(Date, nullable=False)
    receiver = Column(String, nullable=False)  # Name or email of payment receiver
    description = Column(Text, nullable=True)

    # Payment status
    is_paid = Column(Boolean, default=False, nullable=False)

    # Invoice file information
    invoice_file_id = Column(
        Integer,
        ForeignKey("files.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Foreign key to lease (optional - some payments might not be tied to a lease)
    lease_id = Column(
        Integer,
        ForeignKey("leases.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    lease = relationship("Lease", back_populates="payments")
    invoice_file = relationship("File", foreign_keys=[invoice_file_id])

    @property
    def status(self) -> str:
        """Calculate payment status based on is_paid and due_date."""
        if self.is_paid:
            return "Paid"

        today = datetime.now().date()
        if self.due_date < today:
            return "Overdue"
        else:
            return "Pending"
