from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.core.logging import get_logger
from api.core.security import get_current_user
from api.src.users.models import User

from .service import PropertyService
from .schemas import PropertyResponse, PropertyBase

logger = get_logger(__name__)
router = APIRouter(prefix="/properties", tags=["properties"])


def get_property_service(session: AsyncSession = Depends(get_session)) -> PropertyService:
    """Dependency for getting property service instance."""
    return PropertyService(session)

@router.get("/", response_model=list[PropertyResponse])
async def get_all_properties(
    service: PropertyService = Depends(get_property_service),
    current_user: User = Depends(get_current_user),
) -> list[PropertyResponse]:
    """Get all properties."""
    logger.debug("Fetching all Properties")
    try:
        properties = await service.get_all_properties()
        logger.info(f"Retrieved {len(properties)} properties")
        return properties
    except Exception as e:
        logger.error(f"Failed to fetch properties: {str(e)}")
        raise


@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: int,
    service: PropertyService = Depends(get_property_service),
    current_user: User = Depends(get_current_user),
) -> PropertyResponse:
    """Get property by ID."""
    logger.debug("Fetching property {property_id}")
    try:
        properties = await service.get_property(property_id)
        logger.info(f"Retrieved  property {property_id}")
        return properties
    except Exception as e:
        logger.error(f"Failed to fetch property {property_id}: {str(e)}")
        raise


@router.post("/", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
async def create_property(
    property_data: PropertyBase,
    service: PropertyService = Depends(get_property_service),
    current_user: User = Depends(get_current_user),
) -> PropertyResponse:
    """Create a new property."""
    logger.debug("Creating new property")
    property_create = property_data.model_copy(update={"owner_id": current_user.id})
    try:
        property_obj = await service.create_property(property_create)
        logger.info(f"Created property {property_obj.id}")
        return property_obj
    except Exception as e:
        logger.error(f"Failed to create property: {str(e)}")
        raise


@router.patch("/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: int,
    property_data: PropertyBase,
    service: PropertyService = Depends(get_property_service),
    current_user: User = Depends(get_current_user),
) -> PropertyResponse:
    """Update property by ID."""
    logger.debug(f"Updating property {property_id}")
    try:
        property_obj = await service.update_property(property_id, property_data)
        logger.info(f"Updated property {property_id}")
        return property_obj
    except Exception as e:
        logger.error(f"Failed to update property {property_id}: {str(e)}")
        raise


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_property(
    property_id: int,
    service: PropertyService = Depends(get_property_service),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete property by ID."""
    logger.debug(f"Deleting property {property_id}")
    try:
        await service.delete_property(property_id)
        logger.info(f"Deleted property {property_id}")
    except Exception as e:
        logger.error(f"Failed to delete property {property_id}: {str(e)}")
        raise
