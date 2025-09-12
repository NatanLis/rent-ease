from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.core.exceptions import AlreadyExistsException, NotFoundException
from api.core.logging import get_logger
from api.src.leases.models import Lease
from api.src.payments.models import Payment
from api.src.payments.schemas import PaymentCreate, PaymentInvoiceUpdate, PaymentUpdate
from api.src.properties.models import Property
from api.src.units.models import Unit

logger = get_logger(__name__)


class PaymentRepository:
    """Repository for payment data access operations."""

    def __init__(self, session: AsyncSession):
        """Initialize PaymentRepository.

        Args:
            session (AsyncSession): SQLAlchemy async session
        """
        self.session = session

    def _get_payment_options(self):
        """Get selectinload options for payments with all relationships."""
        from api.src.leases.models import Lease
        from api.src.units.models import Unit

        return [
            selectinload(Payment.lease).selectinload(Lease.user),
            selectinload(Payment.lease)
            .selectinload(Lease.unit)
            .selectinload(Unit.property),
            selectinload(Payment.invoice_file),
        ]

    async def create(self, data: PaymentCreate) -> Payment:
        """Create a new payment.

        Args:
            data (PaymentCreate): Payment creation data

        Returns:
            Payment: Created payment with relationships loaded

        Raises:
            AlreadyExistsException: If payment creation fails due to constraints
        """
        payment = Payment(**data.model_dump())
        self.session.add(payment)

        try:
            await self.session.commit()
            await self.session.refresh(payment)

            # Load relationships
            stmt = (
                select(Payment)
                .options(*self._get_payment_options())
                .where(Payment.id == payment.id)
            )
            result = await self.session.execute(stmt)
            payment = result.scalar_one()

            logger.info(f"Created payment: {payment.id}")
            return payment
        except IntegrityError as e:
            await self.session.rollback()
            raise AlreadyExistsException("Payment creation failed") from e

    async def get_by_id(self, payment_id: int) -> Payment:
        """Get payment by ID with relationships loaded.

        Args:
            payment_id (int): Payment ID

        Returns:
            Payment: Payment with relationships

        Raises:
            NotFoundException: If payment not found
        """
        stmt = (
            select(Payment)
            .options(*self._get_payment_options())
            .where(Payment.id == payment_id)
        )
        result = await self.session.execute(stmt)
        payment = result.scalar_one_or_none()

        if not payment:
            raise NotFoundException(f"Payment {payment_id} not found")

        return payment

    async def get_all(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> list[Payment]:
        """Get all payments with relationships loaded.

        Args:
            limit (Optional[int]): Maximum number of results
            offset (Optional[int]): Number of results to skip

        Returns:
            list[Payment]: List of payments with relationships
        """
        stmt = (
            select(Payment)
            .options(*self._get_payment_options())
            .order_by(Payment.created_at.desc())
        )

        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_lease_id(self, lease_id: int) -> list[Payment]:
        """Get all payments for a specific lease.

        Args:
            lease_id (int): Lease ID

        Returns:
            list[Payment]: List of payments for the lease
        """
        stmt = (
            select(Payment)
            .options(*self._get_payment_options())
            .where(Payment.lease_id == lease_id)
            .order_by(Payment.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_tenant_id(self, tenant_id: int) -> list[Payment]:
        """Get all payments for a specific tenant.

        Args:
            tenant_id (int): Tenant ID

        Returns:
            list[Payment]: List of payments for the tenant
        """
        stmt = (
            select(Payment)
            .join(Payment.lease)
            .options()
            .where(Payment.lease.tenant_id == tenant_id)
            .order_by(Payment.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_status(
        self, is_paid: bool, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> list[Payment]:
        """Get payments by payment status.

        Args:
            is_paid (bool): Payment status
            limit (Optional[int]): Maximum number of results
            offset (Optional[int]): Number of results to skip

        Returns:
            list[Payment]: List of payments with the specified status
        """
        stmt = (
            select(Payment)
            .options()
            .where(Payment.is_paid == is_paid)
            .order_by(Payment.created_at.desc())
        )

        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_overdue_payments(
        self, as_of_date: Optional[date] = None
    ) -> list[Payment]:
        """Get overdue payments (unpaid and past due date).

        Args:
            as_of_date (Optional[date]): Date to check against (defaults to today)

        Returns:
            list[Payment]: List of overdue payments
        """
        if as_of_date is None:
            as_of_date = date.today()

        stmt = (
            select(Payment)
            .options()
            .where(~Payment.is_paid, Payment.due_date < as_of_date)
            .order_by(Payment.due_date.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, payment_id: int, data: PaymentUpdate) -> Payment:
        """Update payment information.

        Args:
            payment_id (int): Payment ID
            data (PaymentUpdate): Updated payment data

        Returns:
            Payment: Updated payment with relationships

        Raises:
            NotFoundException: If payment not found
        """
        payment = await self.get_by_id(payment_id)
        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            return payment

        for field, value in update_data.items():
            setattr(payment, field, value)

        await self.session.commit()
        await self.session.refresh(payment)

        # Reload with relationships
        updated_payment = await self.get_by_id(payment_id)
        logger.info(f"Updated payment: {payment_id}")
        return updated_payment

    async def mark_as_paid(self, payment_id: int) -> Payment:
        """Mark payment as paid.

        Args:
            payment_id (int): Payment ID

        Returns:
            Payment: Updated payment

        Raises:
            NotFoundException: If payment not found
        """
        payment = await self.get_by_id(payment_id)
        payment.is_paid = True

        await self.session.commit()
        await self.session.refresh(payment)

        updated_payment = await self.get_by_id(payment_id)
        logger.info(f"Marked payment as paid: {payment_id}")
        return updated_payment

    async def mark_as_unpaid(self, payment_id: int) -> Payment:
        """Mark payment as unpaid.

        Args:
            payment_id (int): Payment ID

        Returns:
            Payment: Updated payment

        Raises:
            NotFoundException: If payment not found
        """
        payment = await self.get_by_id(payment_id)
        payment.is_paid = False

        await self.session.commit()
        await self.session.refresh(payment)

        updated_payment = await self.get_by_id(payment_id)
        logger.info(f"Marked payment as unpaid: {payment_id}")
        return updated_payment

    async def attach_invoice(
        self, payment_id: int, invoice_data: PaymentInvoiceUpdate
    ) -> Payment:
        """Attach invoice file to payment.

        Args:
            payment_id (int): Payment ID
            invoice_data (PaymentInvoiceUpdate): Invoice file data

        Returns:
            Payment: Updated payment with invoice

        Raises:
            NotFoundException: If payment not found
        """
        payment = await self.get_by_id(payment_id)
        payment.invoice_file_id = invoice_data.invoice_file_id

        await self.session.commit()
        await self.session.refresh(payment)

        updated_payment = await self.get_by_id(payment_id)
        logger.info(f"Attached invoice to payment: {payment_id}")
        return updated_payment

    async def delete(self, payment_id: int) -> None:
        """Delete a payment.

        Args:
            payment_id (int): Payment ID

        Raises:
            NotFoundException: If payment not found
        """
        payment = await self.get_by_id(payment_id)

        await self.session.delete(payment)
        await self.session.commit()

        logger.info(f"Deleted payment: {payment_id}")

    async def count_total(self) -> int:
        """Get total count of payments.

        Returns:
            int: Total number of payments
        """
        stmt = select(Payment.id)
        result = await self.session.execute(stmt)
        return len(result.scalars().all())

    async def count_by_status(self, is_paid: bool) -> int:
        """Get count of payments by status.

        Args:
            is_paid (bool): Payment status

        Returns:
            int: Number of payments with the specified status
        """
        stmt = select(Payment.id).where(Payment.is_paid == is_paid)
        result = await self.session.execute(stmt)
        return len(result.scalars().all())

    async def get_by_property_owner(
        self, owner_id: int, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> list[Payment]:
        """Get all payments for properties owned by a specific owner.

        Args:
            owner_id (int): Property owner ID
            limit (Optional[int]): Maximum number of results
            offset (Optional[int]): Number of results to skip

        Returns:
            list[Payment]: List of payments for the owner's properties
        """
        from api.src.leases.models import Lease
        from api.src.properties.models import Property
        from api.src.units.models import Unit

        stmt = (
            select(Payment)
            .join(Payment.lease)
            .join(Lease.unit)
            .join(Unit.property)
            .options()
            .where(Property.owner_id == owner_id)
            .order_by(Payment.created_at.desc())
        )

        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_property_owner_and_status(
        self,
        owner_id: int,
        is_paid: bool,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[Payment]:
        """Get payments by property owner and payment status.

        Args:
            owner_id (int): Property owner ID
            is_paid (bool): Payment status
            limit (Optional[int]): Maximum number of results
            offset (Optional[int]): Number of results to skip

        Returns:
            list[Payment]: List of payments for the owner's properties with specified status
        """
        from api.src.leases.models import Lease
        from api.src.properties.models import Property
        from api.src.units.models import Unit

        stmt = (
            select(Payment)
            .join(Payment.lease)
            .join(Lease.unit)
            .join(Unit.property)
            .options()
            .where(Property.owner_id == owner_id, Payment.is_paid == is_paid)
            .order_by(Payment.created_at.desc())
        )

        if limit is not None:
            stmt = stmt.limit(limit)
        if offset is not None:
            stmt = stmt.offset(offset)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_overdue_payments_by_owner(
        self, owner_id: int, as_of_date: Optional[date] = None
    ) -> list[Payment]:
        """Get overdue payments for properties owned by a specific owner.

        Args:
            owner_id (int): Property owner ID
            as_of_date (Optional[date]): Date to check against (defaults to today)

        Returns:
            list[Payment]: List of overdue payments for the owner's properties
        """
        from api.src.leases.models import Lease
        from api.src.properties.models import Property
        from api.src.units.models import Unit

        if as_of_date is None:
            as_of_date = date.today()

        stmt = (
            select(Payment)
            .join(Payment.lease)
            .join(Lease.unit)
            .join(Unit.property)
            .options()
            .where(
                Property.owner_id == owner_id,
                ~Payment.is_paid,
                Payment.due_date < as_of_date,
            )
            .order_by(Payment.due_date.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_total_for_owner(self, owner_id: int) -> int:
        """Get total count of payments for properties owned by a specific owner.

        Args:
            owner_id (int): Property owner ID

        Returns:
            int: Total number of payments for the owner's properties
        """
        stmt = (
            select(Payment.id)
            .select_from(Payment)
            .join(Lease, Payment.lease_id == Lease.id)
            .join(Unit, Lease.unit_id == Unit.id)
            .join(Property, Unit.property_id == Property.id)
            .where(Property.owner_id == owner_id)
        )
        result = await self.session.execute(stmt)
        return len(result.scalars().all())

    async def count_by_status_for_owner(self, owner_id: int, is_paid: bool) -> int:
        """Get count of payments by status for properties owned by a specific owner.

        Args:
            owner_id (int): Property owner ID
            is_paid (bool): Payment status

        Returns:
            int: Number of payments with the specified status for the owner's properties
        """
        stmt = (
            select(Payment.id)
            .select_from(Payment)
            .join(Lease, Payment.lease_id == Lease.id)
            .join(Unit, Lease.unit_id == Unit.id)
            .join(Property, Unit.property_id == Property.id)
            .where(Property.owner_id == owner_id, Payment.is_paid == is_paid)
        )
        result = await self.session.execute(stmt)
        return len(result.scalars().all())
