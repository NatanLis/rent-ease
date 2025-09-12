from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.core.logging import get_logger
from api.core.security import get_current_user
from api.src.enums.enums_user_role import EnumUserRoles
from api.src.payments.schemas import (
    PaymentCreate,
    PaymentInvoiceUpdate,
    PaymentResponse,
    PaymentStatusUpdate,
    PaymentUpdate,
    RecurringPaymentCreate,
    RecurringPaymentResponse,
)
from api.src.payments.service import PaymentService
from api.src.users.models import User

logger = get_logger(__name__)
router = APIRouter(prefix="/payments", tags=["payments"])


def get_payment_service(
    session: AsyncSession = Depends(get_session),
) -> PaymentService:
    """Get payment service instance."""
    return PaymentService(session)


@router.post(
    "/",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_payment(
    payment_data: PaymentCreate,
    service: PaymentService = Depends(get_payment_service),
    current_user: User = Depends(get_current_user),
) -> PaymentResponse:
    """Create a new payment.

    Requires: ADMIN or OWNER role
    """
    if current_user.role not in [EnumUserRoles.ADMIN, EnumUserRoles.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create payments",
        )

    logger.info(f"Creating payment by user {current_user.id}")
    return await service.create_payment(payment_data)


@router.get(
    "/",
    response_model=list[PaymentResponse],
)
async def get_payments(
    limit: Optional[int] = Query(
        None, ge=1, le=100, description="Maximum number of results"
    ),
    offset: Optional[int] = Query(None, ge=0, description="Number of results to skip"),
    status_filter: Optional[str] = Query(
        None, regex="^(paid|unpaid|overdue)$", description="Filter by payment status"
    ),
    lease_id: Optional[int] = Query(None, description="Filter by lease ID"),
    tenant_id: Optional[int] = Query(None, description="Filter by tenant ID"),
    service: PaymentService = Depends(get_payment_service),
    current_user: User = Depends(get_current_user),
) -> list[PaymentResponse]:
    """Get payments with optional filtering.

    Supports filtering by:
    - status: paid, unpaid, overdue
    - lease_id: specific lease
    - tenant_id: specific tenant

    Tenants can only see their own payments.
    """
    logger.info(
        f"Getting payments for user {current_user.id} with filters: status={status_filter}, lease_id={lease_id}, tenant_id={tenant_id}"
    )

    # If user is tenant, they can only see their own payments
    if current_user.role == EnumUserRoles.TENANT:
        return await service.get_payments_by_tenant(current_user.id)

    # Apply filters based on query parameters
    if tenant_id:
        return await service.get_payments_by_tenant(tenant_id)

    if lease_id:
        return await service.get_payments_by_lease(lease_id)

    # Handle status filters with owner/admin logic
    if status_filter == "paid":
        if current_user.role == EnumUserRoles.OWNER:
            return await service.get_payments_for_owner_by_status(
                current_user.id, True, limit=limit, offset=offset
            )
        return await service.get_payments_by_status(True, limit=limit, offset=offset)
    elif status_filter == "unpaid":
        if current_user.role == EnumUserRoles.OWNER:
            return await service.get_payments_for_owner_by_status(
                current_user.id, False, limit=limit, offset=offset
            )
        return await service.get_payments_by_status(False, limit=limit, offset=offset)
    elif status_filter == "overdue":
        if current_user.role == EnumUserRoles.OWNER:
            return await service.get_overdue_payments_for_owner(current_user.id)
        return await service.get_overdue_payments()

    # Default: get all payments based on user role
    if current_user.role == EnumUserRoles.OWNER:
        return await service.get_payments_for_owner(
            current_user.id, limit=limit, offset=offset
        )

    # ADMIN gets all payments
    return await service.get_all_payments(limit=limit, offset=offset)


@router.get(
    "/statistics",
    response_model=dict,
)
async def get_payment_statistics(
    service: PaymentService = Depends(get_payment_service),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get payment statistics.

    Returns counts for total, paid, pending, and overdue payments.
    Requires: ADMIN or OWNER role
    """
    if current_user.role not in [EnumUserRoles.ADMIN, EnumUserRoles.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view payment statistics",
        )

    logger.info(f"Getting payment statistics for user {current_user.id}")

    # If user is OWNER, get statistics only for their properties
    if current_user.role == EnumUserRoles.OWNER:
        return await service.get_payment_statistics_for_owner(current_user.id)

    # ADMIN gets all statistics
    return await service.get_payment_statistics()


@router.get(
    "/overdue",
    response_model=list[PaymentResponse],
)
async def get_overdue_payments(
    service: PaymentService = Depends(get_payment_service),
    current_user: User = Depends(get_current_user),
) -> list[PaymentResponse]:
    """Get all overdue payments.

    Requires: ADMIN or OWNER role
    """
    if current_user.role not in [EnumUserRoles.ADMIN, EnumUserRoles.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view overdue payments",
        )

    logger.info(f"Getting overdue payments for user {current_user.id}")
    return await service.get_overdue_payments()


@router.get(
    "/{payment_id}",
    response_model=PaymentResponse,
)
async def get_payment(
    payment_id: int,
    service: PaymentService = Depends(get_payment_service),
    current_user: User = Depends(get_current_user),
) -> PaymentResponse:
    """Get payment by ID.

    Tenants can only access their own payments.
    """
    payment = await service.get_payment(payment_id)

    # Check if tenant is trying to access someone else's payment
    if (
        current_user.role == EnumUserRoles.TENANT
        and payment.lease
        and payment.lease.tenant_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this payment",
        )

    logger.info(f"Getting payment {payment_id} for user {current_user.id}")
    return payment


@router.put(
    "/{payment_id}",
    response_model=PaymentResponse,
)
async def update_payment(
    payment_id: int,
    payment_data: PaymentUpdate,
    service: PaymentService = Depends(get_payment_service),
    current_user: User = Depends(get_current_user),
) -> PaymentResponse:
    """Update payment information.

    Requires: ADMIN or OWNER role
    """
    if current_user.role not in [EnumUserRoles.ADMIN, EnumUserRoles.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update payments",
        )

    logger.info(f"Updating payment {payment_id} by user {current_user.id}")
    return await service.update_payment(payment_id, payment_data)


@router.patch(
    "/{payment_id}/status",
    response_model=PaymentResponse,
)
async def update_payment_status(
    payment_id: int,
    status_data: PaymentStatusUpdate,
    service: PaymentService = Depends(get_payment_service),
    current_user: User = Depends(get_current_user),
) -> PaymentResponse:
    """Update payment status (mark as paid/unpaid).

    Requires: ADMIN or OWNER role
    """
    if current_user.role not in [EnumUserRoles.ADMIN, EnumUserRoles.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update payment status",
        )

    logger.info(
        f"Updating payment {payment_id} status to {status_data.is_paid} by user {current_user.id}"
    )

    if status_data.is_paid:
        return await service.mark_payment_as_paid(payment_id)
    else:
        return await service.mark_payment_as_unpaid(payment_id)


@router.patch(
    "/{payment_id}/mark-paid",
    response_model=PaymentResponse,
)
async def mark_payment_as_paid(
    payment_id: int,
    service: PaymentService = Depends(get_payment_service),
    current_user: User = Depends(get_current_user),
) -> PaymentResponse:
    """Mark payment as paid.

    Requires: ADMIN or OWNER role
    """
    if current_user.role not in [EnumUserRoles.ADMIN, EnumUserRoles.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to mark payments as paid",
        )

    logger.info(f"Marking payment {payment_id} as paid by user {current_user.id}")
    return await service.mark_payment_as_paid(payment_id)


@router.patch(
    "/{payment_id}/mark-unpaid",
    response_model=PaymentResponse,
)
async def mark_payment_as_unpaid(
    payment_id: int,
    service: PaymentService = Depends(get_payment_service),
    current_user: User = Depends(get_current_user),
) -> PaymentResponse:
    """Mark payment as unpaid.

    Requires: ADMIN or OWNER role
    """
    if current_user.role not in [EnumUserRoles.ADMIN, EnumUserRoles.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to mark payments as unpaid",
        )

    logger.info(f"Marking payment {payment_id} as unpaid by user {current_user.id}")
    return await service.mark_payment_as_unpaid(payment_id)


@router.patch(
    "/{payment_id}/attach-invoice",
    response_model=PaymentResponse,
)
async def attach_invoice_to_payment(
    payment_id: int,
    invoice_data: PaymentInvoiceUpdate,
    service: PaymentService = Depends(get_payment_service),
    current_user: User = Depends(get_current_user),
) -> PaymentResponse:
    """Attach invoice file to payment.

    Requires: ADMIN or OWNER role
    """
    if current_user.role not in [EnumUserRoles.ADMIN, EnumUserRoles.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to attach invoices to payments",
        )

    logger.info(f"Attaching invoice to payment {payment_id} by user {current_user.id}")
    return await service.attach_invoice_to_payment(payment_id, invoice_data)


@router.delete(
    "/{payment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_payment(
    payment_id: int,
    service: PaymentService = Depends(get_payment_service),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a payment.

    Requires: ADMIN or OWNER role
    """
    if current_user.role not in [EnumUserRoles.ADMIN, EnumUserRoles.OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete payments",
        )

    logger.info(f"Deleting payment {payment_id} by user {current_user.id}")
    await service.delete_payment(payment_id)


@router.get(
    "/lease/{lease_id}",
    response_model=list[PaymentResponse],
)
async def get_payments_by_lease(
    lease_id: int,
    service: PaymentService = Depends(get_payment_service),
    current_user: User = Depends(get_current_user),
) -> list[PaymentResponse]:
    """Get all payments for a specific lease.

    Tenants can only access payments for their own leases.
    """
    payments = await service.get_payments_by_lease(lease_id)

    # Check if tenant is trying to access payments for someone else's lease
    if current_user.role == EnumUserRoles.TENANT:
        for payment in payments:
            if payment.lease and payment.lease.tenant_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to view payments for this lease",
                )

    logger.info(f"Getting payments for lease {lease_id} by user {current_user.id}")
    return payments


@router.get(
    "/tenant/{tenant_id}",
    response_model=list[PaymentResponse],
)
async def get_payments_by_tenant(
    tenant_id: int,
    service: PaymentService = Depends(get_payment_service),
    current_user: User = Depends(get_current_user),
) -> list[PaymentResponse]:
    """Get all payments for a specific tenant.

    Tenants can only access their own payments.
    Requires: ADMIN, OWNER role or tenant accessing own payments
    """
    # Check if tenant is trying to access someone else's payments
    if current_user.role == EnumUserRoles.TENANT and tenant_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view payments for this tenant",
        )

    # For non-tenants, check proper authorization
    if current_user.role not in [
        EnumUserRoles.ADMIN,
        EnumUserRoles.OWNER,
        EnumUserRoles.TENANT,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view tenant payments",
        )

    logger.info(f"Getting payments for tenant {tenant_id} by user {current_user.id}")
    return await service.get_payments_by_tenant(tenant_id)


@router.post(
    "/recurring",
    response_model=RecurringPaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_recurring_payments(
    recurring_data: RecurringPaymentCreate,
    service: PaymentService = Depends(get_payment_service),
    current_user: User = Depends(get_current_user),
) -> RecurringPaymentResponse:
    """Create recurring payments for a lease.

    Creates multiple payments based on frequency (monthly, quarterly, yearly)
    and distributes the total amount across the lease duration.

    Requires: ADMIN, OWNER, or OWNER role
    """
    if current_user.role not in [
        EnumUserRoles.ADMIN,
        EnumUserRoles.OWNER,
        EnumUserRoles.OWNER,
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create recurring payments",
        )

    logger.info(
        f"Creating recurring payments for lease {recurring_data.lease_id} "
        f"by user {current_user.id}"
    )

    try:
        return await service.create_recurring_payments(recurring_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        logger.error(f"Error creating recurring payments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create recurring payments",
        ) from e
