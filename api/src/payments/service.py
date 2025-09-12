from datetime import date
from typing import Optional

from dateutil.relativedelta import relativedelta
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.leases.repository import LeaseRepository
from api.src.payments.repository import PaymentRepository
from api.src.payments.schemas import (
    PaymentCreate,
    PaymentFrequency,
    PaymentInvoiceUpdate,
    PaymentResponse,
    PaymentUpdate,
    RecurringPaymentCreate,
    RecurringPaymentResponse,
)


class PaymentService:
    """Service layer for payment business logic."""

    def __init__(self, session: AsyncSession):
        """Initialize PaymentService.

        Args:
            session (AsyncSession): SQLAlchemy async session
        """
        self.session = session
        self.repository = PaymentRepository(session)

    async def create_payment(self, payment_data: PaymentCreate) -> PaymentResponse:
        """Create a new payment.

        Args:
            payment_data (PaymentCreate): Payment creation data

        Returns:
            PaymentResponse: Created payment response
        """
        payment = await self.repository.create(payment_data)
        return PaymentResponse.model_validate(payment)

    async def get_payment(self, payment_id: int) -> PaymentResponse:
        """Get payment by ID.

        Args:
            payment_id (int): Payment ID

        Returns:
            PaymentResponse: Payment response
        """
        payment = await self.repository.get_by_id(payment_id)
        return PaymentResponse.model_validate(payment)

    async def get_all_payments(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> list[PaymentResponse]:
        """Get all payments.

        Args:
            limit (Optional[int]): Maximum number of results
            offset (Optional[int]): Number of results to skip

        Returns:
            list[PaymentResponse]: List of payment responses
        """
        payments = await self.repository.get_all(limit=limit, offset=offset)
        return [PaymentResponse.model_validate(payment) for payment in payments]

    async def get_payments_by_lease(self, lease_id: int) -> list[PaymentResponse]:
        """Get all payments for a specific lease.

        Args:
            lease_id (int): Lease ID

        Returns:
            list[PaymentResponse]: List of payment responses for the lease
        """
        payments = await self.repository.get_by_lease_id(lease_id)
        return [PaymentResponse.model_validate(payment) for payment in payments]

    async def get_payments_by_tenant(self, tenant_id: int) -> list[PaymentResponse]:
        """Get all payments for a specific tenant.

        Args:
            tenant_id (int): Tenant ID

        Returns:
            list[PaymentResponse]: List of payment responses for the tenant
        """
        payments = await self.repository.get_by_tenant_id(tenant_id)
        return [PaymentResponse.model_validate(payment) for payment in payments]

    async def get_payments_by_status(
        self, is_paid: bool, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> list[PaymentResponse]:
        """Get payments by payment status.

        Args:
            is_paid (bool): Payment status
            limit (Optional[int]): Maximum number of results
            offset (Optional[int]): Number of results to skip

        Returns:
            list[PaymentResponse]: List of payment responses with specified status
        """
        payments = await self.repository.get_by_status(
            is_paid, limit=limit, offset=offset
        )
        return [PaymentResponse.model_validate(payment) for payment in payments]

    async def get_overdue_payments(
        self, as_of_date: Optional[date] = None
    ) -> list[PaymentResponse]:
        """Get overdue payments.

        Args:
            as_of_date (Optional[date]): Date to check against (defaults to today)

        Returns:
            list[PaymentResponse]: List of overdue payment responses
        """
        payments = await self.repository.get_overdue_payments(as_of_date)
        return [PaymentResponse.model_validate(payment) for payment in payments]

    async def update_payment(
        self, payment_id: int, payment_data: PaymentUpdate
    ) -> PaymentResponse:
        """Update payment information.

        Args:
            payment_id (int): Payment ID
            payment_data (PaymentUpdate): Updated payment data

        Returns:
            PaymentResponse: Updated payment response
        """
        payment = await self.repository.update(payment_id, payment_data)
        return PaymentResponse.model_validate(payment)

    async def mark_payment_as_paid(self, payment_id: int) -> PaymentResponse:
        """Mark payment as paid.

        Args:
            payment_id (int): Payment ID

        Returns:
            PaymentResponse: Updated payment response
        """
        payment = await self.repository.mark_as_paid(payment_id)
        return PaymentResponse.model_validate(payment)

    async def mark_payment_as_unpaid(self, payment_id: int) -> PaymentResponse:
        """Mark payment as unpaid.

        Args:
            payment_id (int): Payment ID

        Returns:
            PaymentResponse: Updated payment response
        """
        payment = await self.repository.mark_as_unpaid(payment_id)
        return PaymentResponse.model_validate(payment)

    async def attach_invoice_to_payment(
        self, payment_id: int, invoice_data: PaymentInvoiceUpdate
    ) -> PaymentResponse:
        """Attach invoice file to payment.

        Args:
            payment_id (int): Payment ID
            invoice_data (PaymentInvoiceUpdate): Invoice file data

        Returns:
            PaymentResponse: Updated payment response
        """
        payment = await self.repository.attach_invoice(payment_id, invoice_data)
        return PaymentResponse.model_validate(payment)

    async def delete_payment(self, payment_id: int) -> None:
        """Delete a payment.

        Args:
            payment_id (int): Payment ID
        """
        await self.repository.delete(payment_id)

    async def get_payment_statistics(self) -> dict:
        """Get payment statistics.

        Returns:
            dict: Dictionary with payment statistics
        """
        total_payments = await self.repository.count_total()
        paid_payments = await self.repository.count_by_status(True)
        unpaid_payments = await self.repository.count_by_status(False)
        overdue_payments = await self.repository.get_overdue_payments()

        return {
            "total_payments": total_payments,
            "paid_count": paid_payments,
            "pending_count": unpaid_payments - len(overdue_payments),
            "overdue_count": len(overdue_payments),
        }

    async def get_payment_statistics_for_owner(self, owner_id: int) -> dict:
        """Get payment statistics for a specific owner.

        Args:
            owner_id (int): Property owner ID

        Returns:
            dict: Dictionary with payment statistics for the owner
        """
        total_payments = await self.repository.count_total_for_owner(owner_id)
        paid_payments = await self.repository.count_by_status_for_owner(owner_id, True)
        unpaid_payments = await self.repository.count_by_status_for_owner(
            owner_id, False
        )
        overdue_payments = await self.repository.get_overdue_payments_by_owner(
            owner_id
        )

        return {
            "total_payments": total_payments,
            "paid_count": paid_payments,
            "pending_count": unpaid_payments - len(overdue_payments),
            "overdue_count": len(overdue_payments),
        }

    async def get_payments_for_owner(
        self, owner_id: int, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> list[PaymentResponse]:
        """Get all payments for properties owned by a specific owner.

        Args:
            owner_id (int): Property owner ID
            limit (Optional[int]): Maximum number of results
            offset (Optional[int]): Number of results to skip

        Returns:
            list[PaymentResponse]: List of payment responses for the owner's properties
        """
        payments = await self.repository.get_by_property_owner(
            owner_id, limit=limit, offset=offset
        )
        return [PaymentResponse.model_validate(payment) for payment in payments]

    async def get_payments_for_owner_by_status(
        self,
        owner_id: int,
        is_paid: bool,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[PaymentResponse]:
        """Get payments for an owner by payment status.

        Args:
            owner_id (int): Property owner ID
            is_paid (bool): Payment status
            limit (Optional[int]): Maximum number of results
            offset (Optional[int]): Number of results to skip

        Returns:
            list[PaymentResponse]: List of payment responses for the owner's properties with specified status
        """
        payments = await self.repository.get_by_property_owner_and_status(
            owner_id, is_paid, limit=limit, offset=offset
        )
        return [PaymentResponse.model_validate(payment) for payment in payments]

    async def get_overdue_payments_for_owner(
        self, owner_id: int, as_of_date: Optional[date] = None
    ) -> list[PaymentResponse]:
        """Get overdue payments for properties owned by a specific owner.

        Args:
            owner_id (int): Property owner ID
            as_of_date (Optional[date]): Date to check against (defaults to today)

        Returns:
            list[PaymentResponse]: List of overdue payment responses for the owner's properties
        """
        payments = await self.repository.get_overdue_payments_by_owner(
            owner_id, as_of_date
        )
        return [PaymentResponse.model_validate(payment) for payment in payments]

    async def create_recurring_payments(
        self, recurring_data: RecurringPaymentCreate
    ) -> RecurringPaymentResponse:
        """Create recurring payments for a lease based on frequency and duration.

        Args:
            recurring_data (RecurringPaymentCreate): Recurring payment creation data

        Returns:
            RecurringPaymentResponse: Response with created payment details
        """
        # First, get the lease to validate it exists and get duration
        lease_repo = LeaseRepository(self.session)
        lease = await lease_repo.get_by_id(recurring_data.lease_id)

        if not lease:
            raise ValueError(f"Lease with ID {recurring_data.lease_id} not found")

        if not lease.is_active:
            raise ValueError("Cannot create payments for inactive lease")

        # Calculate payment schedule
        start_date = lease.start_date
        end_date = lease.end_date or date.today().replace(year=date.today().year + 1)

        payment_dates = self._calculate_payment_dates(
            start_date, end_date, recurring_data.frequency, recurring_data.due_day
        )

        # Calculate amount per payment
        amount_per_payment = self._calculate_payment_amount(
            recurring_data.amount, len(payment_dates), recurring_data.frequency
        )

        # Create payments
        created_payments = []
        for i, payment_date in enumerate(payment_dates):
            # For the last payment, adjust amount to handle any remainder from division
            if i == len(payment_dates) - 1:
                remaining_amount = recurring_data.amount - (
                    amount_per_payment * (len(payment_dates) - 1)
                )
                current_amount = remaining_amount
            else:
                current_amount = amount_per_payment

            payment_data = PaymentCreate(
                document_type=recurring_data.document_type,
                gross_value=current_amount,
                due_date=payment_date,
                receiver=f"{lease.user.first_name} {lease.user.last_name}",
                description=recurring_data.description
                or f"{recurring_data.frequency.value.title()} payment",
                lease_id=recurring_data.lease_id,
            )

            payment = await self.repository.create(payment_data)
            created_payments.append(payment.id)

        return RecurringPaymentResponse(
            lease_id=recurring_data.lease_id,
            payments_created=len(created_payments),
            total_amount=recurring_data.amount,
            frequency=recurring_data.frequency,
            due_day=recurring_data.due_day,
            payments=created_payments,
        )

    def _calculate_payment_dates(
        self,
        start_date: date,
        end_date: date,
        frequency: PaymentFrequency,
        due_day: int,
    ) -> list[date]:
        """Calculate payment due dates based on frequency and lease duration."""
        payment_dates = []

        # Calculate the first payment date
        current_date = start_date.replace(
            day=min(due_day, 28)
        )  # Safe day to avoid month overflow

        # Adjust first payment to the due day
        if current_date.day != due_day:
            # Try to set the exact due day, but handle month overflow
            try:
                current_date = current_date.replace(day=due_day)
            except ValueError:
                # If due_day doesn't exist in current month (e.g., day 31 in February),
                # use the last day of the month
                next_month = current_date.replace(day=28) + relativedelta(days=4)
                current_date = (
                    next_month - relativedelta(days=next_month.day)
                ).replace(
                    day=min(
                        due_day, (next_month - relativedelta(days=next_month.day)).day
                    )
                )

        # If the first payment date is before the start date, move to next period
        if current_date < start_date:
            if frequency == PaymentFrequency.MONTHLY:
                current_date += relativedelta(months=1)
            elif frequency == PaymentFrequency.QUARTERLY:
                current_date += relativedelta(months=3)
            elif frequency == PaymentFrequency.YEARLY:
                current_date += relativedelta(years=1)

        # Generate payment dates until end of lease
        while current_date <= end_date:
            payment_dates.append(current_date)

            if frequency == PaymentFrequency.MONTHLY:
                current_date += relativedelta(months=1)
            elif frequency == PaymentFrequency.QUARTERLY:
                current_date += relativedelta(months=3)
            elif frequency == PaymentFrequency.YEARLY:
                current_date += relativedelta(years=1)

            # Handle day overflow for next month
            try:
                current_date = current_date.replace(day=due_day)
            except ValueError:
                # Use last day of month if due_day doesn't exist
                next_month = current_date.replace(day=28) + relativedelta(days=4)
                last_day = (next_month - relativedelta(days=next_month.day)).day
                current_date = current_date.replace(day=min(due_day, last_day))

        return payment_dates

    def _calculate_payment_amount(
        self, total_amount: float, num_payments: int, frequency: PaymentFrequency
    ) -> float:
        """Calculate the amount per payment, handling division remainders."""
        if num_payments == 0:
            return 0.0

        # For most payments, use the divided amount
        base_amount = total_amount / num_payments

        # Round to 2 decimal places to handle currency
        return round(base_amount, 2)
