from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Header
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.core.logging import get_logger
from api.core.security import get_current_user
from api.src.users.models import User

from .service import ProfilePictureService
from .schemas import ProfilePictureResponse, ProfilePictureCreate

logger = get_logger(__name__)
router = APIRouter(prefix="/profile-pictures", tags=["profile-pictures"])


def get_profile_picture_service(session: AsyncSession = Depends(get_session)) -> ProfilePictureService:
    """Dependency for getting profile picture service instance."""
    return ProfilePictureService(session)


@router.post("/upload", response_model=ProfilePictureResponse, status_code=status.HTTP_201_CREATED)
async def upload_profile_picture(
    file: UploadFile = File(...),
    x_user_id: str = Header(..., alias="X-User-ID"),
    service: ProfilePictureService = Depends(get_profile_picture_service),
) -> ProfilePictureResponse:
    """Upload a new profile picture."""
    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID"
        )
    
    logger.debug(f"Uploading profile picture for user {user_id}: {file.filename}")
    
    try:
        # Read file data
        file_data = await file.read()
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only JPG, PNG, and GIF are allowed."
            )
        
        # Validate file size (1MB max)
        max_size = 1024 * 1024  # 1MB
        if len(file_data) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large. Maximum size is 1MB."
            )
        
        # Create profile picture object
        profile_picture_create = ProfilePictureCreate(
            filename=file.filename or "profile_picture",
            mimetype=file.content_type or "application/octet-stream",
            size=len(file_data),
            data=file_data
        )
        
        profile_picture = await service.create_profile_picture(user_id, profile_picture_create)
        logger.info(f"Uploaded profile picture {profile_picture.id} for user {user_id}")
        return profile_picture
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload profile picture for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload profile picture"
        )


@router.get("/{profile_picture_id}", response_model=ProfilePictureResponse)
async def get_profile_picture(
    profile_picture_id: int,
    service: ProfilePictureService = Depends(get_profile_picture_service),
) -> ProfilePictureResponse:
    """Get profile picture by ID."""
    logger.debug(f"Fetching profile picture {profile_picture_id}")
    
    try:
        profile_picture = await service.get_profile_picture(profile_picture_id)
        if not profile_picture:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile picture not found"
            )
        
        logger.info(f"Retrieved profile picture {profile_picture_id}")
        return profile_picture
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch profile picture {profile_picture_id}: {str(e)}")
        raise


@router.get("/{profile_picture_id}/download")
async def download_profile_picture(
    profile_picture_id: int,
    service: ProfilePictureService = Depends(get_profile_picture_service),
):
    """Download profile picture by ID."""
    logger.debug(f"Downloading profile picture {profile_picture_id}")
    
    try:
        profile_picture_download = await service.get_profile_picture_for_download(profile_picture_id)
        if not profile_picture_download:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile picture not found"
            )
        
        logger.info(f"Downloaded profile picture {profile_picture_id}: {profile_picture_download.filename}")
        return Response(
            content=profile_picture_download.data,
            media_type=profile_picture_download.mimetype,
            headers={"Content-Disposition": f"inline; filename={profile_picture_download.filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to download profile picture {profile_picture_id}: {str(e)}")
        raise


@router.delete("/{profile_picture_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile_picture(
    profile_picture_id: int,
    service: ProfilePictureService = Depends(get_profile_picture_service),
) -> None:
    """Delete profile picture by ID."""
    logger.debug(f"Deleting profile picture {profile_picture_id}")
    
    try:
        success = await service.delete_profile_picture(profile_picture_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile picture not found"
            )
        logger.info(f"Deleted profile picture {profile_picture_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete profile picture {profile_picture_id}: {str(e)}")
        raise
