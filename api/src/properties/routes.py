from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.core.logging import get_logger
from api.core.security import get_current_user
from api.src.enums.enums_user_role import EnumUserRoles
from api.src.properties.schemas import PropertyBase, PropertyResponse, PropertyUpdate
from api.src.properties.service import PropertyService
from api.src.users.models import User
from api.src.utils.access_verify import is_owner_or_admin

logger = get_logger(__name__)
router = APIRouter(prefix="/properties", tags=["properties"])


def get_property_service(
    session: AsyncSession = Depends(get_session),
) -> PropertyService:
    return PropertyService(session)


@router.get(
    "/",
    response_model=list[PropertyResponse],
)
async def get_all_properties(
    service: PropertyService = Depends(get_property_service),
    current_user: User = Depends(get_current_user),
) -> list[PropertyResponse]:
    properties = []
    if current_user.role == EnumUserRoles.ADMIN:
        properties = await service.get_all_properties()
    else:
        properties = await service.get_properties_for_owner(current_user.id)
    return properties


@router.get(
    "/owner",
    response_model=list[PropertyResponse],
)
async def get_owner_properties(
    service: PropertyService = Depends(get_property_service),
    current_user: User = Depends(get_current_user),
) -> list[PropertyResponse]:
    is_owner_or_admin(current_user)

    properties = await service.get_properties_for_owner(current_user.id)
    return properties


@router.get(
    "/{property_id}",
    response_model=PropertyResponse,
)
async def get_property(
    property_id: int,
    service: PropertyService = Depends(get_property_service),
    current_user: User = Depends(get_current_user),
) -> PropertyResponse:
    properties = await service.get_property(property_id)
    return properties


@router.post(
    "/",
    response_model=PropertyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_property(
    property_data: PropertyBase,
    service: PropertyService = Depends(get_property_service),
    current_user: User = Depends(get_current_user),
) -> PropertyResponse:
    property_create = property_data.model_copy(update={"owner_id": current_user.id})
    property_obj = await service.create_property(property_create)
    return property_obj


@router.patch(
    "/{property_id}",
    response_model=PropertyResponse,
)
async def update_property(
    property_id: int,
    property_data: PropertyUpdate,
    service: PropertyService = Depends(get_property_service),
    current_user: User = Depends(get_current_user),
) -> PropertyResponse:
    property_obj = await service.update_property(property_id, property_data)
    return property_obj


@router.delete(
    "/{property_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_property(
    property_id: int,
    service: PropertyService = Depends(get_property_service),
    current_user: User = Depends(get_current_user),
) -> None:
    await service.delete_property(property_id)
