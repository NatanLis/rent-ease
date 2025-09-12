from sqlalchemy.ext.asyncio import AsyncSession

from api.src.leases.repository import LeaseRepository
from api.src.leases.schemas import LeaseCreate, LeaseEnd, LeaseResponse
from api.src.properties.repository import PropertyRepository
from api.src.units.repository import UnitRepository


class LeaseService:
    def __init__(self, session: AsyncSession):
        self.repository = LeaseRepository(session)
        self.unit_repository = UnitRepository(session)
        self.property_repository = PropertyRepository(session)

    async def create_lease(
        self,
        lease_data: LeaseCreate,
    ) -> LeaseResponse:
        lease = await self.repository.create(lease_data)
        return LeaseResponse.model_validate(lease)

    async def end_lease(
        self,
        lease_id: int,
        end_data: LeaseEnd,
    ) -> LeaseResponse:
        lease = await self.repository.end_lease(lease_id, end_data.end_date)
        return LeaseResponse.model_validate(lease)

    async def activate_lease(
        self,
        lease_id: int,
    ) -> LeaseResponse:
        lease = await self.repository.activate_lease(lease_id)
        return LeaseResponse.model_validate(lease)

    async def get_lease(
        self,
        lease_id: int,
    ) -> LeaseResponse:
        lease = await self.repository.get_by_id(lease_id)
        return LeaseResponse.model_validate(lease)

    async def get_all_leases(self) -> list[LeaseResponse]:
        leases = await self.repository.get_all()
        result = []
        for lease in leases:
            lease_dict = LeaseResponse.model_validate(lease).model_dump()
            if lease.user and lease.user.profile_picture_id:
                lease_dict["user"]["avatar_url"] = (
                    f"/api/profile-pictures/{lease.user.profile_picture_id}/download"
                )
            result.append(LeaseResponse(**lease_dict))
        return result

    async def list_leases_for_tenant(
        self,
        tenant_id: int,
    ) -> list[LeaseResponse]:
        leases = await self.repository.list_for_tenant(tenant_id)
        result = []
        for lease in leases:
            lease_dict = LeaseResponse.model_validate(lease).model_dump()
            if lease.user and lease.user.profile_picture_id:
                lease_dict["user"]["avatar_url"] = (
                    f"/api/profile-pictures/{lease.user.profile_picture_id}/download"
                )
            result.append(LeaseResponse(**lease_dict))
        return result

    async def list_leases_for_property_owner(
        self,
        owner_id: int,
    ) -> list[LeaseResponse]:
        leases = await self.repository.list_for_property_owner(owner_id)
        result = []
        for lease in leases:
            lease_dict = LeaseResponse.model_validate(lease).model_dump()
            # Generate avatar_url if user has profile picture
            if lease.user and lease.user.profile_picture_id:
                lease_dict["user"]["avatar_url"] = (
                    f"/api/profile-pictures/{lease.user.profile_picture_id}/download"
                )
            result.append(LeaseResponse(**lease_dict))
        return result

    async def get_unit_by_id(self, unit_id: int):
        """Get unit by ID - used for validation in lease creation."""
        return await self.unit_repository.get_by_id(unit_id)

    async def get_property_by_id(self, property_id: int):
        """Get property by ID - used for validation in lease creation."""
        return await self.property_repository.get_by_id(property_id)
