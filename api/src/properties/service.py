from sqlalchemy.ext.asyncio import AsyncSession

from api.core.logging import get_logger
from api.src.properties.repository import PropertyRepository
from api.src.properties.schemas import PropertyCreate, PropertyResponse, PropertyBase

logger = get_logger(__name__)


class PropertyService:
    """Service for handling property business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = PropertyRepository(session)

    async def create_property(self, property_data: PropertyCreate) -> PropertyResponse:
        """Create a new Property.

        Args:
            property_data: Property creation data

        Returns:
            PropertyResponse: Created property data
        """
        return await self.repository.create(property_data)

    async def get_property_by_id(self, property_id: int) -> PropertyResponse:
        """Get property by ID.

        Args:
            property_id: Property ID

        Returns:
            PropertyResponse: Found property
        """
        return await self.repository.get_by_id(property_id)

    async def get_all_properties(self) -> list[PropertyResponse]:
        """Get all properties.

        Returns:
            List[properties]: List of all properties
        """
        properties = await self.repository.get_all()
        return [PropertyResponse.model_validate(property) for property in properties]

    async def update_property(self, property_id: int, property_data: PropertyBase) -> PropertyResponse:
        """Update property by ID.

        Args:
            property_id: Property ID
            property_data: Property update data

        Returns:
            Property: Updated property data
        """
        property_obj = await self.repository.update(property_id, property_data)
        return property_obj

    async def delete_property(self, property_id: int) -> None:
        """Delete property by ID.

        Args:
            property_id: Property ID
        """
        await self.repository.delete(property_id)

