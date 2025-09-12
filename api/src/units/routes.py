from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.core.logging import get_logger
from api.core.security import get_current_user
from api.src.enums.enums_user_role import EnumUserRoles
from api.src.properties.repository import PropertyRepository
from api.src.units.schemas import UnitCreate, UnitResponse, UnitUpdate
from api.src.units.service import UnitService
from api.src.users.models import User
from api.src.utils.access_verify import is_authorized_user

logger = get_logger(__name__)
router = APIRouter(prefix="/units", tags=["units"])


def get_unit_service(
    session: AsyncSession = Depends(get_session),
) -> UnitService:
    return UnitService(session)


@router.post(
    "/",
    response_model=UnitResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_unit(
    unit_data: UnitCreate,
    service: UnitService = Depends(get_unit_service),
    current_user: User = Depends(get_current_user),
) -> UnitResponse:
    property_repo = PropertyRepository(service.repository.session)
    prop = await property_repo.get_by_id(unit_data.property_id)
    is_authorized_user(current_user, prop, detail="Not authorized to create unit")
    return await service.create_unit(unit_data)


@router.get(
    "/",
    response_model=list[UnitResponse],
)
async def get_all_units(
    service: UnitService = Depends(get_unit_service),
    current_user: User = Depends(get_current_user),
) -> list[UnitResponse]:
    """Get all units. Admins see all units, owners see only their units."""
    if current_user.role == EnumUserRoles.ADMIN:
        return await service.get_all_units()
    else:
        # For owners, we need to filter units by their properties
        # This would require a more complex query, for now return all
        # TODO: Implement filtering by owner's properties
        return await service.get_all_units()


@router.get(
    "/property/{property_id}",
    response_model=list[UnitResponse],
)
async def list_units(
    property_id: int,
    service: UnitService = Depends(get_unit_service),
) -> list[UnitResponse]:
    return await service.list_units_for_property(property_id)


@router.delete(
    "/{unit_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_unit(
    unit_id: int,
    service: UnitService = Depends(get_unit_service),
    current_user: User = Depends(get_current_user),
):
    logger.debug(f"User {current_user.id} is attempting to delete unit {unit_id}")
    unit = await service.get_unit(unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    property_repo = PropertyRepository(service.repository.session)
    prop = await property_repo.get_by_id(unit.property_id)
    is_authorized_user(current_user, prop, detail="Not authorized to delete this unit")
    await service.delete_unit(unit_id)


@router.patch("/{unit_id}", response_model=UnitResponse)
async def update_unit(
    unit_id: int,
    unit_data: UnitUpdate,
    service: UnitService = Depends(get_unit_service),
    current_user: User = Depends(get_current_user),
):
    """Update a unit by ID."""
    logger.debug(f"User {current_user.id} is attempting to update unit {unit_id}")
    unit = await service.get_unit(unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    # Only owner or admin can update the unit
    property_repo = PropertyRepository(service.repository.session)
    prop = await property_repo.get_by_id(unit.property_id)
    is_authorized_user(current_user, prop, detail="Not authorized to update this unit")
    return await service.update_unit(unit_id, unit_data)
