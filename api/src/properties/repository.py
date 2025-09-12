from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.core.exceptions import (
    AlreadyExistsException,
    ConflictException,
    NotFoundException,
)
from api.src.properties.models import Property
from api.src.properties.schemas import PropertyCreate
from api.src.units.models import Unit


class PropertyRepository:
    """Repository for handling property database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        property_data: PropertyCreate,
    ) -> Property:
        new_property = Property(**property_data.model_dump(exclude_unset=True))

        try:
            self.session.add(new_property)
            await self.session.commit()
            await self.session.refresh(new_property)
            return new_property
        except IntegrityError:
            await self.session.rollback()
            raise AlreadyExistsException(
                f"Property with alias {new_property.title} already exists"
            ) from None

    async def get_by_id(self, property_id: int) -> Property:
        query = (
            select(Property)
            .where(Property.id == property_id)
            .options(selectinload(Property.units).selectinload(Unit.leases))
        )
        result = await self.session.execute(query)
        property_obj = result.scalar_one_or_none()

        if not property_obj:
            raise NotFoundException("Property not found")

        # Calculate units_count and active_leases
        property_obj.units_count = len(property_obj.units)
        property_obj.active_leases = sum(
            1
            for unit in property_obj.units
            if any(lease.is_active for lease in unit.leases)
        )

        return property_obj

    async def get_all(self) -> list[Property]:
        query = select(Property).options(
            selectinload(Property.units).selectinload(Unit.leases)
        )
        result = await self.session.execute(query)
        properties = list(result.scalars().all())

        # Calculate units_count and active_leases for each property
        for prop in properties:
            prop.units_count = len(prop.units)
            prop.active_leases = sum(
                1
                for unit in prop.units
                if any(lease.is_active for lease in unit.leases)
            )

        return properties

    async def get_by_owner(
        self,
        owner_id: int,
    ) -> list[Property]:
        # Load properties with their units and leases to calculate counts
        query = (
            select(Property)
            .where(Property.owner_id == owner_id)
            .options(selectinload(Property.units).selectinload(Unit.leases))
        )
        result = await self.session.execute(query)
        properties = list(result.scalars().all())

        # Calculate units_count and active_leases for each property
        for prop in properties:
            prop.units_count = len(prop.units)
            prop.active_leases = sum(
                1
                for unit in prop.units
                if any(lease.is_active for lease in unit.leases)
            )

        return properties

    async def update(
        self,
        property_id: int,
        property_data,
    ) -> Property:
        update_data = property_data.model_dump(exclude_unset=True)
        if not update_data:
            raise ValueError("No fields to update")

        query = (
            update(Property).where(Property.id == property_id).values(**update_data)
        )
        result = await self.session.execute(query)

        if not result.rowcount:
            raise NotFoundException(f"Property with id {property_id} not found")

        await self.session.commit()
        return await self.get_by_id(property_id)

    async def delete(
        self,
        property_id: int,
    ) -> None:
        # First, check if property exists and load with units and leases
        property_query = (
            select(Property)
            .where(Property.id == property_id)
            .options(selectinload(Property.units).selectinload(Unit.leases))
        )
        result = await self.session.execute(property_query)
        property_obj = result.scalar_one_or_none()

        if not property_obj:
            raise NotFoundException(f"Property with id {property_id} not found")

        # Check if any unit has active leases
        active_leases_count = sum(
            1
            for unit in property_obj.units
            if any(lease.is_active for lease in unit.leases)
        )

        if active_leases_count > 0:
            raise ConflictException(
                f"Cannot delete property. It has {active_leases_count} active lease(s). "
                "Please terminate all active leases before deleting the property."
            )

        # If no active leases, proceed with deletion
        query = delete(Property).where(Property.id == property_id)
        await self.session.execute(query)
        await self.session.commit()
