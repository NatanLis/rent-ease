from sqlalchemy.ext.asyncio import AsyncSession

from .repository import UnitRepository
from .schemas import UnitCreate, UnitUpdate, UnitResponse


class UnitService:
    def __init__(self, session: AsyncSession):
        self.repository = UnitRepository(session)

    async def create_unit(self, data: UnitCreate) -> UnitResponse:
        """
        Create a new Unit.

        Args:
            data: Unit creation data

        Returns:
            UnitResponse: Created unit data
        """
        unit = await self.repository.create(data)
        return UnitResponse.model_validate(unit)

    async def get_unit(self, unit_id: int) -> UnitResponse:
        """
        Retrieve a Unit by its ID.

        Args:
            unit_id: ID of the unit to retrieve

        Returns:
            UnitResponse: Retrieved unit data
        """
        unit = await self.repository.get_by_id(unit_id)
        return UnitResponse.model_validate(unit)

    async def list_units_for_property(self, property_id: int) -> list[UnitResponse]:
        """
        List all Units for a given Property.

        Args:
            property_id: ID of the property to list units for

        Returns:
            list[UnitResponse]: List of units for the property
        """
        units = await self.repository.list_by_property(property_id)
        return [UnitResponse.model_validate(u) for u in units]

    async def update_unit(self, unit_id: int, data: UnitUpdate) -> UnitResponse:
        """
        Update an existing Unit.

        Args:
            unit_id: ID of the unit to update
            data: Unit update data

        Returns:
            UnitResponse: Updated unit data
        """
        unit = await self.repository.update(unit_id, data)
        return UnitResponse.model_validate(unit)

    async def delete_unit(self, unit_id: int) -> None:
        """
        Delete a Unit by its ID.

        Args:
            unit_id: ID of the unit to delete

        Returns:
            None
        """
        await self.repository.delete(unit_id)
