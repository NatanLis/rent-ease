from sqlalchemy.ext.asyncio import AsyncSession

from api.src.units.repository import UnitRepository
from api.src.units.schemas import UnitCreate, UnitResponse, UnitUpdate


class UnitService:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.repository = UnitRepository(session)

    async def create_unit(
        self,
        data: UnitCreate,
    ) -> UnitResponse:
        unit = await self.repository.create(data)
        return UnitResponse.model_validate(unit)

    async def get_unit(
        self,
        unit_id: int,
    ) -> UnitResponse:
        unit = await self.repository.get_by_id(unit_id)
        return UnitResponse.model_validate(unit)

    async def get_all_units(self) -> list[UnitResponse]:
        """Get all units with property details."""
        units = await self.repository.get_all()

        result = []
        for unit in units:
            # Calculate active leases count
            active_leases = (
                sum(1 for lease in unit.leases if lease.is_active)
                if unit.leases
                else 0
            )

            # Determine status based on active leases
            status = "occupied" if active_leases > 0 else "available"

            # Create response with additional fields
            unit_data = unit.__dict__.copy()
            unit_data.update(
                {
                    "property_title": unit.property.title
                    if unit.property
                    else "Unknown Property",
                    "property_address": unit.property.address
                    if unit.property
                    else "Unknown Address",
                    "active_leases": active_leases,
                    "status": status,
                }
            )

            result.append(UnitResponse.model_validate(unit_data))

        return result

    async def list_units_for_property(
        self,
        property_id: int,
    ) -> list[UnitResponse]:
        units = await self.repository.list_by_property(property_id)
        return [UnitResponse.model_validate(u) for u in units]

    async def update_unit(
        self,
        unit_id: int,
        data: UnitUpdate,
    ) -> UnitResponse:
        unit = await self.repository.update(unit_id, data)
        return UnitResponse.model_validate(unit)

    async def delete_unit(
        self,
        unit_id: int,
    ) -> None:
        await self.repository.delete(unit_id)
