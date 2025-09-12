from fastapi import HTTPException, status

from api.core.logging import get_logger
from api.src.enums.enums_user_role import EnumUserRoles
from api.src.properties.models import Property
from api.src.users.models import User

logger = get_logger(__name__)


def is_owner_or_admin(current_user: User) -> None:
    if current_user.role not in [EnumUserRoles.ADMIN, EnumUserRoles.OWNER]:
        logger.warning(
            f"Access denied for user {current_user.email} with role {current_user.role}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return None


def is_authorized_user(current_user: User, prop: Property, detail: str) -> None:
    if (
        current_user.role not in [EnumUserRoles.ADMIN]
        and prop.owner_id != current_user.id
    ):
        raise HTTPException(status_code=403, detail=detail)
    return None
