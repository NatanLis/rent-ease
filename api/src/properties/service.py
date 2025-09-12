from sqlalchemy.ext.asyncio import AsyncSession

from api.core.logging import get_logger
from api.src.properties.repository import PropertyRepository
from api.src.properties.schemas import PropertyCreate, PropertyResponse, PropertyUpdate

logger = get_logger(__name__)


class PropertyService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = PropertyRepository(session)

    async def create_property(self, property_data: PropertyCreate) -> PropertyResponse:
        return await self.repository.create(property_data)

    async def get_property_by_id(self, property_id: int) -> PropertyResponse:
        return await self.repository.get_by_id(property_id)

    async def get_all_properties(self) -> list[PropertyResponse]:
        properties = await self.repository.get_all()
        return [PropertyResponse.model_validate(property) for property in properties]

    async def get_properties_for_owner(self, owner_id: int) -> list[PropertyResponse]:
        properties = await self.repository.get_by_owner(owner_id)
        return [PropertyResponse.model_validate(property) for property in properties]

    async def update_property(
        self,
        property_id: int,
        property_data: PropertyUpdate,
    ) -> PropertyResponse:
        property_obj = await self.repository.update(property_id, property_data)
        return property_obj

    async def delete_property(self, property_id: int) -> None:
        await self.repository.delete(property_id)
