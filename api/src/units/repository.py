from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from .models import Unit
from .schemas import UnitCreate, UnitUpdate
from api.core.exceptions import NotFoundException, AlreadyExistsException


class UnitRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: UnitCreate) -> Unit:
        """Create a new unit.

        Args:
            data (UnitCreate): Unit creation data.

        Returns:
            Unit: Created unit.

        Raises:
            AlreadyExistsException: If a unit with the same name already exists on the property.
        """
        unit = Unit(**data.model_dump())
        self.session.add(unit)
        try:
            await self.session.commit()
            await self.session.refresh(unit)
            return unit
        except IntegrityError as e:
            await self.session.rollback()
            raise AlreadyExistsException(f"Unit with name '{data.name}' already exists on that property") from e

    async def get_by_id(self, unit_id: int) -> Unit:
        """Get a unit by its ID.

        Args:
            unit_id (int): The ID of the unit.

        Returns:
            Unit: The unit with the given ID.

        Raises:
            NotFoundException: If the unit does not exist.
        """
        unit = await self.session.get(Unit, unit_id)
        if not unit:
            raise NotFoundException(f"Unit {unit_id} not found")
        return unit

    async def get_all(self) -> list[Unit]:
        """Get all units.

        Returns:
            list[Unit]: List of all units.
        """
        result = await self.session.execute(
            select(Unit)
            .options(
                selectinload(Unit.property),
                selectinload(Unit.leases)
            )
        )
        return result.scalars().all()

    async def get_by_owner(self, owner_id: int) -> list[Unit]:
        """Get all units for properties owned by a specific user.

        Args:
            owner_id (int): The ID of the owner.

        Returns:
            list[Unit]: List of units belonging to owner's properties.
        """
        from api.src.properties.models import Property
        result = await self.session.execute(
            select(Unit)
            .join(Property, Unit.property_id == Property.id)
            .where(Property.owner_id == owner_id)
            .options(
                selectinload(Unit.property),
                selectinload(Unit.leases)
            )
        )
        return result.scalars().all()

    async def list_by_property(self, property_id: int) -> list[Unit]:
        """List all units for a given property.

        Args:
            property_id (int): The ID of the property.

        Returns:
            list[Unit]: List of units belonging to the property.
        """
        result = await self.session.execute(select(Unit).where(Unit.property_id == property_id))
        return result.scalars().all()

    async def update(self, unit_id: int, data: UnitUpdate) -> Unit:
        """Update an existing unit.

        Args:
            unit_id (int): The ID of the unit to update.
            data (UnitUpdate): The data to update the unit with.

        Returns:
            Unit: The updated unit.

        Raises:
            NotFoundException: If the unit does not exist.
        """
        unit = await self.get_by_id(unit_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(unit, field, value)
        self.session.add(unit)
        await self.session.commit()
        await self.session.refresh(unit)
        return unit

    async def delete(self, unit_id: int) -> None:
        """Delete a unit by its ID.

        Args:
            unit_id (int): The ID of the unit to delete.

        Raises:
            NotFoundException: If the unit does not exist.
        """
        unit = await self.get_by_id(unit_id)
        await self.session.delete(unit)
        await self.session.commit()
