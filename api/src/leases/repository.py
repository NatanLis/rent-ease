from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.core.exceptions import (
    AlreadyExistsException,
    BusinessRuleViolationException,
    NotFoundException,
)
from api.src.leases.models import Lease
from api.src.leases.schemas import LeaseCreate
from api.src.properties.models import Property
from api.src.units.models import Unit


def overlaps(existing_start, existing_end, new_start, new_end):
    """Check if two date ranges overlap.

    Args:
        existing_start (date): Start date of existing lease
        existing_end (date or None): End date of existing lease (None means ongoing)
        new_start (date): Start date of new lease
        new_end (date or None): End date of new lease (None means ongoing)

    Returns:
        bool: True if the date ranges overlap, False otherwise
    """
    # If existing lease has no end date (ongoing), it conflicts if new lease starts before infinity
    if existing_end is None:
        return new_start >= existing_start

    # If new lease has no end date (ongoing), it conflicts if it starts before existing lease ends
    if new_end is None:
        return new_start <= existing_end

    # Both leases have end dates - check for standard overlap
    # No overlap if: new_end < existing_start OR new_start > existing_end
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
        stmt = select(Lease).where(
            Lease.unit_id == data.unit_id,
            Lease.is_active,
        )
        result = await self.session.execute(stmt)
        existing_leases = result.scalars().all()

        for lease in existing_leases:
            if overlaps(
                lease.start_date, lease.end_date, data.start_date, data.end_date
            ):
                existing_period = f"{lease.start_date}"
                if lease.end_date:
                    existing_period += f" to {lease.end_date}"
                else:
                    existing_period += " (ongoing)"

                new_period = f"{data.start_date}"
                if data.end_date:
                    new_period += f" to {data.end_date}"
                else:
                    new_period += " (ongoing)"

                raise BusinessRuleViolationException(
                    f"Cannot create lease for period {new_period}. "
                    f"This unit already has an active lease for period {existing_period}."
                )

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

            stmt = (
                select(Lease)
                .options(
                    selectinload(Lease.user),
                    selectinload(Lease.unit).selectinload(Unit.property),
                )
                .where(Lease.id == lease.id)
            )
            result = await self.session.execute(stmt)
            lease = result.scalar_one()

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
            Lease: Updated lease with eager loaded relationships

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

        # Reload with eager loading for serialization
        result = await self.session.execute(
            select(Lease)
            .options(
                selectinload(Lease.user),
                selectinload(Lease.unit).selectinload(Unit.property),
            )
            .where(Lease.id == lease_id)
        )
        return result.scalar_one()

    async def activate_lease(self, lease_id: int) -> Lease:
        """Activate a lease by setting it to active status.

        Args:
            lease_id (int): ID of the lease to activate

        Returns:
            Lease: Updated lease with eager loaded relationships

        Raises:
            NotFoundException: If lease with given ID is not found
        """
        lease = await self.session.get(Lease, lease_id)
        if not lease:
            raise NotFoundException(f"Lease {lease_id} not found")
        lease.is_active = True
        self.session.add(lease)
        await self.session.commit()
        await self.session.refresh(lease)

        # Reload with eager loading for serialization
        result = await self.session.execute(
            select(Lease)
            .options(
                selectinload(Lease.user),
                selectinload(Lease.unit).selectinload(Unit.property),
            )
            .where(Lease.id == lease_id)
        )
        return result.scalar_one()

    async def get_by_id(self, lease_id: int) -> Lease:
        """Retrieve a lease by its ID.

        Args:
            lease_id (int): ID of the lease

        Returns:
            Lease: Lease with the given ID

        Raises:
            NotFoundException: If lease with given ID is not found
        """
        stmt = (
            select(Lease)
            .options(
                selectinload(Lease.user),
                selectinload(Lease.unit).selectinload(Unit.property),
            )
            .where(Lease.id == lease_id)
        )

        result = await self.session.execute(stmt)
        lease = result.scalar_one_or_none()

        if not lease:
            raise NotFoundException(f"Lease {lease_id} not found")
        return lease

    async def get_all(self) -> list[Lease]:
        """Get all leases with related data.

        Returns:
            list[Lease]: List of all leases with unit, user, and property data
        """
        result = await self.session.execute(
            select(Lease).options(
                selectinload(Lease.user),
                selectinload(Lease.unit).selectinload(Unit.property),
            )
        )
        return result.scalars().all()

    async def list_for_tenant(self, tenant_id: int) -> list[Lease]:
        """List all leases for a given tenant.

        Args:
            tenant_id (int): ID of the tenant

        Returns:
            list[Lease]: List of leases for the tenant
        """
        result = await self.session.execute(
            select(Lease)
            .where(Lease.tenant_id == tenant_id)
            .options(
                selectinload(Lease.user),
                selectinload(Lease.unit).selectinload(Unit.property),
            )
        )
        return result.scalars().all()

    async def list_for_property_owner(self, owner_id: int) -> list[Lease]:
        """List all leases for properties owned by a given user.

        Args:
            owner_id (int): ID of the property owner

        Returns:
            list[Lease]: List of leases for properties owned by the user
        """
        result = await self.session.execute(
            select(Lease)
            .join(Unit, Lease.unit_id == Unit.id)
            .join(Property, Unit.property_id == Property.id)
            .where(Property.owner_id == owner_id)
            .options(
                selectinload(Lease.user),
                selectinload(Lease.unit).selectinload(Unit.property),
            )
        )
        return result.scalars().all()
