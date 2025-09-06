from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.core.logging import get_logger
from api.core.security import get_current_user
from api.src.users.models import User
from api.src.users.service import UserService
from api.src.users.schemas import UserResponse, UserUpdate

logger = get_logger(__name__)
router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("/", response_model=list[UserResponse])
async def get_tenants_for_owner(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[UserResponse]:
    """Get all tenant users who have leases in current user's properties."""
    logger.debug(f"Getting tenants for owner user_id={current_user.id}")
    
    # Only admin and owners can view tenants
    if current_user.role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # For admin, get all tenants; for owner, get only tenants in their properties
    if current_user.role == "admin":
        tenants = await UserService(session).get_all_tenants_with_status()
    else:
        tenants = await UserService(session).get_tenants_for_owner(current_user.id)
    
    return [UserResponse.model_validate(tenant) for tenant in tenants]


@router.get("/{tenant_id}", response_model=UserResponse)
async def get_tenant(
    tenant_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get a specific tenant by ID."""
    logger.debug(f"Getting tenant {tenant_id} for user_id={current_user.id}")
    
    # Only admin and owners can view tenants
    if current_user.role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Get tenant
    tenant = await UserService(session).get_user(tenant_id)
    if not tenant or tenant.role != "tenant":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # For owner, check if tenant has leases in their properties
    if current_user.role == "owner":
        tenants_in_properties = await UserService(session).get_tenants_for_owner(current_user.id)
        if not any(t.id == tenant_id for t in tenants_in_properties):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this tenant"
            )
    
    return UserResponse.model_validate(tenant)


@router.put("/{tenant_id}", response_model=UserResponse)
async def update_tenant(
    tenant_id: int,
    tenant_data: UserUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Update a specific tenant by ID."""
    logger.debug(f"Updating tenant {tenant_id} by user_id={current_user.id}")
    
    # Only admin and owners can update tenants
    if current_user.role not in ["admin", "owner"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Get tenant
    tenant = await UserService(session).get_user(tenant_id)
    if not tenant or tenant.role != "tenant":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # For owner, check if tenant has leases in their properties
    if current_user.role == "owner":
        tenants_in_properties = await UserService(session).get_tenants_for_owner(current_user.id)
        if not any(t.id == tenant_id for t in tenants_in_properties):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this tenant"
            )
    
    # Update tenant
    updated_tenant = await UserService(session).update_user(tenant_id, tenant_data)
    logger.info(f"Updated tenant {tenant_id}")
    
    return UserResponse.model_validate(updated_tenant)


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(
    tenant_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a specific tenant by ID."""
    logger.debug(f"Deleting tenant {tenant_id} by user_id={current_user.id}")
    
    # Only admin can delete tenants
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Get tenant
    tenant = await UserService(session).get_user(tenant_id)
    if not tenant or tenant.role != "tenant":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Delete tenant
    await UserService(session).delete_user(tenant_id)
    logger.info(f"Deleted tenant {tenant_id}")
