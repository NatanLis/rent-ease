from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from datetime import date

from .models import Lease
from .schemas import LeaseCreate
from api.core.exceptions import NotFoundException, AlreadyExistsException, BusinessRuleViolationException


def overlaps(existing_start, existing_end, new_start, new_end):
    """Check if two date ranges overlap.

    Args:
        existing_start (date): Start date of existing lease
        existing_end (date or None): End date of existing lease
        new_start (date): Start date of new lease
        new_end (date or None): End date of new lease

    Returns:
        bool: True if the date ranges overlap, False otherwise
    """
    # treat None end as infinity
    if existing_end is None:
        return new_start <= date.max
    if new_end is None:
        return existing_start <= date.max
    return not (new_end < existing_start or new_start > existing_end)


class LeaseRepository:
    def __init__(self, session: AsyncSession):
        """Initialize LeaseRepository.

        Args:
            session (AsyncSession): SQLAlchemy async session
        """
        self.session = session

    async def create(self, data: LeaseCreate) -> Lease:
        """Create a new lease.

        Args:
            data (LeaseCreate): Lease creation data

        Returns:
            Lease: Created lease

        Raises:
            BusinessRuleViolationException: If overlapping active lease exists for this unit
            AlreadyExistsException: If lease already exists (integrity error)
        """
        # check for overlapping active lease on the same unit
        stmt = select(Lease).where(
            Lease.unit_id == data.unit_id,
            Lease.is_active,
        )
        result = await self.session.execute(stmt)
        existing_leases = result.scalars().all()
        for lease in existing_leases:
            if overlaps(lease.start_date, lease.end_date, data.start_date, data.end_date):
                raise BusinessRuleViolationException("Overlapping active lease exists for this unit")

        lease = Lease(
            unit_id=data.unit_id,
            tenant_id=data.tenant_id,
            start_date=data.start_date,
            end_date=data.end_date,
            is_active=True,
        )
        self.session.add(lease)
        try:
            await self.session.commit()
            await self.session.refresh(lease)
            return lease
        except IntegrityError as e:
            await self.session.rollback()
            raise AlreadyExistsException("Lease already exists") from e

    async def end_lease(self, lease_id: int, end_date: date) -> Lease:
        """End an active lease by setting its end date and marking it inactive.

        Args:
            lease_id (int): ID of the lease to end
            end_date (date): End date to set

        Returns:
            Lease: Updated lease

        Raises:
            NotFoundException: If lease with given ID is not found
        """
        lease = await self.session.get(Lease, lease_id)
        if not lease:
            raise NotFoundException(f"Lease {lease_id} not found")
        lease.end_date = end_date
        lease.is_active = False
        self.session.add(lease)
        await self.session.commit()
        await self.session.refresh(lease)
        return lease

    async def get_by_id(self, lease_id: int) -> Lease:
        """Retrieve a lease by its ID.

        Args:
            lease_id (int): ID of the lease

        Returns:
            Lease: Lease with the given ID

        Raises:
            NotFoundException: If lease with given ID is not found
        """
        lease = await self.session.get(Lease, lease_id)
        if not lease:
            raise NotFoundException(f"Lease {lease_id} not found")
        return lease

    async def list_for_tenant(self, tenant_id: int) -> list[Lease]:
        """List all leases for a given tenant.

        Args:
            tenant_id (int): ID of the tenant

        Returns:
            list[Lease]: List of leases for the tenant
        """
        result = await self.session.execute(select(Lease).where(Lease.tenant_id == tenant_id))
        return result.scalars().all()
