from sqlalchemy.ext.asyncio import AsyncSession

from .repository import LeaseRepository
from .schemas import LeaseCreate, LeaseEnd, LeaseResponse


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

    async def list_leases_for_tenant(self, tenant_id: int) -> list[LeaseResponse]:
        """List all leases for a specific tenant.
        Args:
            tenant_id: Tenant ID to filter leases

        Returns:
            list[LeaseResponse]: List of leases for the tenant
        """
        leases = await self.repository.list_for_tenant(tenant_id)
        return [LeaseResponse.model_validate(leas) for leas in leases]
