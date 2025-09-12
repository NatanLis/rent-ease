from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.core.logging import get_logger
from api.core.security import get_current_user
from api.src.enums.enums_user_role import EnumUserRoles
from api.src.users.models import User
from api.src.users.schemas import UserResponse
from api.src.users.service import UserService
from api.src.utils.access_verify import is_owner_or_admin

logger = get_logger(__name__)


users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get("/", response_model=list[UserResponse])
async def get_all_users(
    role: Optional[str] = Query(
        None, description="Filter by role (ADMIN, OWNER, TENANT)"
    ),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[UserResponse]:
    is_owner_or_admin(current_user)

    if current_user.role == EnumUserRoles.ADMIN:
        users = await UserService(session).get_all_users(role)
    else:
        if role and role.lower() != EnumUserRoles.TENANT:
            users = []
        else:
            users = await UserService(session).get_tenants_for_owner(current_user.id)

    result = []
    for user in users:
        user_dict = UserResponse.model_validate(user).model_dump()
        if user.profile_picture_id:
            user_dict["avatar_url"] = (
                f"/api/profile-pictures/{user.profile_picture_id}/download"
            )
        result.append(UserResponse(**user_dict))

    return result
