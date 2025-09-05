from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from api.core.exceptions import AlreadyExistsException, NotFoundException
from .models import Property
from .schemas import PropertyCreate, PropertyUpdate


class PropertyRepository:
    """Repository for handling property database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, property_data: PropertyCreate) -> Property:
        """Create a new property.

        Args:
            property_data: Property creation data

        Returns:
            Property: Created property

        Raises:
            AlreadyExistsException: If property with same unique field already exists
        """

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
            )

    async def get_by_id(self, property_id: int) -> Property:
        """Get property by ID.

        Args:
            property_id: Property ID

        Returns:
            Property: Found property

        Raises:
            NotFoundException: If property not found
        """
        query = select(Property).where(Property.id == property_id)
        result = await self.session.execute(query)
        property_obj = result.scalar_one_or_none()

        if not property_obj:
            raise NotFoundException("Property not found")

        return property_obj

    async def get_all(self) -> list[Property]:
        """Get all properties.

        Returns:
            List[Property]: List of all properties
        """
        query = select(Property)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update(self, property_id: int, property_data) -> PropertyUpdate:
        """Update property by ID.

        Args:
            property_id: Property ID
            property_data: Property update data

        Returns:
            Property: Updated property

        Raises:
            NotFoundException: If property not found
        """
        update_data = property_data.model_dump(exclude_unset=True)
        if not update_data:
            raise ValueError("No fields to update")

        query = update(Property).where(Property.id == property_id).values(**update_data)
        result = await self.session.execute(query)

        if result.rowcount == 0:
            raise NotFoundException(f"Property with id {property_id} not found")

        await self.session.commit()
        return await self.get_by_id(property_id)

    async def delete(self, property_id: int) -> None:
        """Delete property by ID.

        Args:
            property_id: Hero ID

        Raises:
            NotFoundException: If property not found
        """
        query = delete(Property).where(Property.id == property_id)
        result = await self.session.execute(query)

        if result.rowcount == 0:
            raise NotFoundException(f"Property with id {property_id} not found")

        await self.session.commit()
