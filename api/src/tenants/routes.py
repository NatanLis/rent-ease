from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.core.logging import get_logger
from api.core.security import get_current_user
from api.src.enums.enums_user_role import EnumUserRoles
from api.src.users.models import User
from api.src.users.schemas import TenantCreate, UserResponse, UserUpdate
from api.src.users.service import UserService
from api.src.utils.access_verify import is_owner_or_admin

logger = get_logger(__name__)
router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant_data: TenantCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    is_owner_or_admin(current_user)

    existing_user = await UserService(session).get_user_by_email(tenant_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    tenant = await UserService(session).create_tenant(tenant_data)
    logger.info(f"Created new tenant {tenant.id} by user {current_user.id}")

    return UserResponse.model_validate(tenant)


@router.get("/", response_model=list[UserResponse])
async def get_tenants_for_owner(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[UserResponse]:
    is_owner_or_admin(current_user)

    if current_user.role == EnumUserRoles.ADMIN:
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
    is_owner_or_admin(current_user)

    tenant = await UserService(session).get_user(tenant_id)
    if not tenant or tenant.role != EnumUserRoles.TENANT:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found"
        )

    if current_user.role == EnumUserRoles.OWNER:
        tenants_in_properties = await UserService(session).get_tenants_for_owner(
            current_user.id
        )
        if not any(t.id == tenant_id for t in tenants_in_properties):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this tenant",
            )

    return UserResponse.model_validate(tenant)


@router.put("/{tenant_id}", response_model=UserResponse)
async def update_tenant(
    tenant_id: int,
    tenant_data: UserUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    is_owner_or_admin(current_user)

    tenant = await UserService(session).get_user(tenant_id)
    if not tenant or tenant.role != EnumUserRoles.TENANT:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found"
        )

    if current_user.role == EnumUserRoles.OWNER:
        tenants_in_properties = await UserService(session).get_tenants_for_owner(
            current_user.id
        )
        if not any(t.id == tenant_id for t in tenants_in_properties):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this tenant",
            )

    updated_tenant = await UserService(session).update_user(tenant_id, tenant_data)
    logger.info(f"Updated tenant {tenant_id}")

    return UserResponse.model_validate(updated_tenant)


@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tenant(
    tenant_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> None:
    if current_user.role != EnumUserRoles.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    tenant = await UserService(session).get_user(tenant_id)
    if not tenant or tenant.role != EnumUserRoles.TENANT:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found"
        )

    await UserService(session).delete_user(tenant_id)
    logger.info(f"Deleted tenant {tenant_id}")
