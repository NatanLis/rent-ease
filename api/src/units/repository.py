from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.core.exceptions import (
    AlreadyExistsException,
    ConflictException,
    NotFoundException,
)
from api.src.units.models import Unit
from api.src.units.schemas import UnitCreate, UnitUpdate


class UnitRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        data: UnitCreate,
    ) -> Unit:
        unit = Unit(**data.model_dump())
        self.session.add(unit)
        try:
            await self.session.commit()
            await self.session.refresh(unit)
            return unit
        except IntegrityError as e:
            await self.session.rollback()
            raise AlreadyExistsException(
                f"Unit with name '{data.name}' already exists on that property"
            ) from e

    async def get_by_id(
        self,
        unit_id: int,
    ) -> Unit:
        unit = await self.session.get(Unit, unit_id)
        if not unit:
            raise NotFoundException(f"Unit {unit_id} not found")
        return unit

    async def get_all(self) -> list[Unit]:
        """Get all units with their property details and leases loaded."""
        result = await self.session.execute(
            select(Unit).options(
                selectinload(Unit.property), selectinload(Unit.leases)
            )
        )
        return list(result.scalars().all())

    async def list_by_property(
        self,
        property_id: int,
    ) -> list[Unit]:
        result = await self.session.execute(
            select(Unit).where(Unit.property_id == property_id)
        )
        return result.scalars().all()

    async def update(
        self,
        unit_id: int,
        data: UnitUpdate,
    ) -> Unit:
        unit = await self.get_by_id(unit_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(unit, field, value)
        self.session.add(unit)
        await self.session.commit()
        await self.session.refresh(unit)
        return unit

    async def delete(
        self,
        unit_id: int,
    ) -> None:
        # First, get the unit with leases loaded to check for active leases
        result = await self.session.execute(
            select(Unit).where(Unit.id == unit_id).options(selectinload(Unit.leases))
        )
        unit = result.scalar_one_or_none()

        if not unit:
            raise NotFoundException(f"Unit {unit_id} not found")

        # Check if unit has active leases
        active_leases_count = (
            sum(1 for lease in unit.leases if lease.is_active) if unit.leases else 0
        )

        if active_leases_count > 0:
            raise ConflictException(
                f"Cannot delete unit. It has {active_leases_count} active lease(s). "
                "Please terminate all active leases before deleting the unit."
            )

        # If no active leases, proceed with deletion
        await self.session.delete(unit)
        await self.session.commit()
