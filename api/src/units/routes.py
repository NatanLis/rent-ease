from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.core.logging import get_logger
from api.core.security import get_current_user
from api.src.users.models import User
from api.src.properties.repository import PropertyRepository

from api.src.enums import EnumUserRoles

from .service import UnitService
from .schemas import UnitCreate, UnitResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/units", tags=["units"])


def get_unit_service(session: AsyncSession = Depends(get_session)) -> UnitService:
    """Dependency for getting unit service instance."""
    return UnitService(session)


@router.post("/", response_model=UnitResponse, status_code=status.HTTP_201_CREATED)
async def create_unit(
    unit_data: UnitCreate,
    service: UnitService = Depends(get_unit_service),
    current_user: User = Depends(get_current_user),
) -> UnitResponse:
    """Create a new unit."""
    logger.debug(f"User {current_user.id} is attempting to create a unit for property {unit_data.property_id}")
    # only owner or admin who owns the property can create units
    property_repo = PropertyRepository(service.repository.session)  # assuming access to session
    prop = await property_repo.get_by_id(unit_data.property_id)
    if current_user.role not in [EnumUserRoles.ADMIN] and prop.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to add unit to this property")
    return await service.create_unit(unit_data)


@router.get("/property/{property_id}", response_model=list[UnitResponse])
async def list_units(property_id: int, service: UnitService = Depends(get_unit_service)) -> list[UnitResponse]:
    """List all units for a given property."""
    logger.debug(f"Listing units for property {property_id}")
    return await service.list_units_for_property(property_id)


@router.delete("/{unit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_unit(
    unit_id: int,
    service: UnitService = Depends(get_unit_service),
    current_user: User = Depends(get_current_user),
):
    """Delete a unit by ID."""
    logger.debug(f"User {current_user.id} is attempting to delete unit {unit_id}")
    unit = await service.get_unit_by_id(unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    # Only owner or admin can delete the unit
    property_repo = PropertyRepository(service.repository.session)
    prop = await property_repo.get_by_id(unit.property_id)
    if current_user.role not in [EnumUserRoles.ADMIN] and prop.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this unit")
    await service.delete_unit(unit_id)


@router.patch("/{unit_id}", response_model=UnitResponse)
async def update_unit(
    unit_id: int,
    unit_data: UnitCreate,
    service: UnitService = Depends(get_unit_service),
    current_user: User = Depends(get_current_user),
):
    """Update a unit by ID."""
    logger.debug(f"User {current_user.id} is attempting to update unit {unit_id}")
    unit = await service.get_unit_by_id(unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    # Only owner or admin can update the unit
    property_repo = PropertyRepository(service.repository.session)
    prop = await property_repo.get_by_id(unit.property_id)
    if current_user.role not in [EnumUserRoles.ADMIN] and prop.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this unit")
    return await service.update_unit(unit_id, unit_data)
