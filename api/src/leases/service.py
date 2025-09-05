from .repository import LeaseRepository
from .schemas import LeaseCreate, LeaseResponse, LeaseEnd
from sqlalchemy.ext.asyncio import AsyncSession


class LeaseService:
    """Repository for handling lease database operations."""
    def __init__(self, session: AsyncSession):
        self.repository = LeaseRepository(session)

    async def create_lease(self, lease_data: LeaseCreate) -> LeaseResponse:
        """Create a new Lease.

        Args:
            lease_data: Lease creation data

        Returns:
            LeaseResponse: Created lease data
        """
        lease = await self.repository.create(lease_data)
        return LeaseResponse.model_validate(lease)

    async def end_lease(self, lease_id: int, end_data: LeaseEnd) -> LeaseResponse:
        """End an existing lease.
        Args:
            lease_id: Lease ID to end
            end_data: Data containing the end date

        Returns:
            LeaseResponse: Updated lease data with end date set
        """
        lease = await self.repository.end_lease(lease_id, end_data.end_date)
        return LeaseResponse.model_validate(lease)

    async def get_lease(self, lease_id: int) -> LeaseResponse:
        """Get lease by ID.
        Args:
            lease_id: Lease ID

        Returns:
            LeaseResponse: Found lease data
        """
        lease = await self.repository.get_by_id(lease_id)
        return LeaseResponse.model_validate(lease)

    async def get_all_leases(self) -> list[LeaseResponse]:
        """Get all leases.
        Returns:
            list[LeaseResponse]: List of all leases
        """
        leases = await self.repository.get_all()
        result = []
        for lease in leases:
            lease_dict = LeaseResponse.model_validate(lease).model_dump()
            # Generate avatar_url if user has profile picture
            if lease.user and lease.user.profile_picture_id:
                lease_dict['user']['avatar_url'] = f"/api/profile-pictures/{lease.user.profile_picture_id}/download"
            result.append(LeaseResponse(**lease_dict))
        return result

    async def list_leases_for_tenant(self, tenant_id: int) -> list[LeaseResponse]:
        """List all leases for a specific tenant.
        Args:
            tenant_id: Tenant ID to filter leases

        Returns:
            list[LeaseResponse]: List of leases for the tenant
        """
        leases = await self.repository.list_for_tenant(tenant_id)
        result = []
        for lease in leases:
            lease_dict = LeaseResponse.model_validate(lease).model_dump()
            # Generate avatar_url if user has profile picture
            if lease.user and lease.user.profile_picture_id:
                lease_dict['user']['avatar_url'] = f"/api/profile-pictures/{lease.user.profile_picture_id}/download"
            result.append(LeaseResponse(**lease_dict))
        return result
