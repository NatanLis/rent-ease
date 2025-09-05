from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.core.logging import get_logger
from api.core.security import get_current_user
from api.src.users.models import User

from .schemas import LeaseCreate, LeaseEnd, LeaseResponse
from .service import LeaseService

logger = get_logger(__name__)
router = APIRouter(prefix="/leases", tags=["leases"])


def get_lease_service(session: AsyncSession = Depends(get_session)) -> LeaseService:
    """Dependency for getting lease service instance."""
    return LeaseService(session)


@router.post("/", response_model=LeaseResponse, status_code=status.HTTP_201_CREATED)
async def create_lease(
    lease_data: LeaseCreate,
    service: LeaseService = Depends(get_lease_service),
    current_user: User = Depends(get_current_user),
):
    """Create a new lease for a unit."""
    logger.debug("Creating lease for unit_id=%s by user_id=%s", lease_data.unit_id, current_user.id)
    # Only owner of the property (via unit) or admin can assign tenant
    unit = await service.get_unit_by_id(lease_data.unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")

    property_ = await service.get_property_by_id(unit.property_id)
    if not property_:
        raise HTTPException(status_code=404, detail="Property not found")

    if not (current_user.is_admin or property_.owner_id == current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to assign tenant to this unit")
    return await service.create_lease(lease_data)


@router.patch("/{lease_id}/end", response_model=LeaseResponse)
async def end_lease(
    lease_id: int,
    end_data: LeaseEnd,
    service: LeaseService = Depends(get_lease_service),
    current_user: User = Depends(get_current_user),
):
    """End an existing lease."""
    logger.debug("Ending lease lease_id=%s by user_id=%s", lease_id, current_user.id)
    return await service.end_lease(lease_id, end_data)


@router.get("/", response_model=list[LeaseResponse])
async def get_all_leases(
    service: LeaseService = Depends(get_lease_service),
    current_user: User = Depends(get_current_user),
):
    """Get all leases."""
    logger.debug("Getting all leases by user_id=%s", current_user.id)
    # Only admin can view all leases
    if current_user.role != "admin":
        logger.warning(f"Access denied for user {current_user.email} with role {current_user.role}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    leases = await service.get_all_leases()
    logger.info(f"Found {len(leases)} leases")
    
    # Log first lease for debugging
    if leases:
        first_lease = leases[0]
        logger.info(f"First lease: id={first_lease.id}, unit_id={first_lease.unit_id}, tenant_id={first_lease.tenant_id}")
    
    return leases


@router.get("/tenant/{tenant_id}", response_model=list[LeaseResponse])
async def list_tenant_leases(
    tenant_id: int,
    service: LeaseService = Depends(get_lease_service),
    current_user: User = Depends(get_current_user),
):
    """List all leases for a tenant."""
    logger.debug("Listing leases for tenant_id=%s by user_id=%s", tenant_id, current_user.id)
    # tenant can see own; owner/admin can query their tenants (enforce outside)
    return await service.list_leases_for_tenant(tenant_id)
