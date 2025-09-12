from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.core.logging import get_logger
from api.src.profile_pictures.schemas import (
    ProfilePictureCreate,
    ProfilePictureResponse,
)
from api.src.profile_pictures.service import ProfilePictureService

logger = get_logger(__name__)
router = APIRouter(prefix="/profile-pictures", tags=["profile-pictures"])


def get_profile_picture_service(
    session: AsyncSession = Depends(get_session),
) -> ProfilePictureService:
    return ProfilePictureService(session)


@router.post(
    "/upload",
    response_model=ProfilePictureResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_profile_picture(
    file: UploadFile = File(...),
    x_user_id: str = Header(..., alias="X-User-ID"),
    service: ProfilePictureService = Depends(get_profile_picture_service),
) -> ProfilePictureResponse:
    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID"
        ) from None

    try:
        file_data = await file.read()
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/gif"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only JPG, PNG, and GIF are allowed.",
            )
        max_size = 1024 * 1024
        if len(file_data) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large. Maximum size is 1MB.",
            )

        profile_picture_create = ProfilePictureCreate(
            filename=file.filename or "profile_picture",
            mimetype=file.content_type or "application/octet-stream",
            size=len(file_data),
            data=file_data,
        )

        profile_picture = await service.create_profile_picture(
            user_id,
            profile_picture_create,
        )
        return profile_picture

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload profile picture for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload profile picture",
        ) from None


@router.get(
    "/{profile_picture_id}",
    response_model=ProfilePictureResponse,
)
async def get_profile_picture(
    profile_picture_id: int,
    service: ProfilePictureService = Depends(get_profile_picture_service),
) -> ProfilePictureResponse:
    try:
        profile_picture = await service.get_profile_picture(profile_picture_id)
        if not profile_picture:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile picture not found",
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
    try:
        profile_picture_download = await service.get_profile_picture_for_download(
            profile_picture_id
        )
        if not profile_picture_download:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile picture not found",
            )

        return Response(
            content=profile_picture_download.data,
            media_type=profile_picture_download.mimetype,
            headers={
                "Content-Disposition": f"inline; filename={profile_picture_download.filename}"
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to download profile picture {profile_picture_id}: {str(e)}"
        )
        raise


@router.delete(
    "/{profile_picture_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_profile_picture(
    profile_picture_id: int,
    service: ProfilePictureService = Depends(get_profile_picture_service),
) -> None:
    try:
        success = await service.delete_profile_picture(profile_picture_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile picture not found",
            )
        logger.info(f"Deleted profile picture {profile_picture_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to delete profile picture {profile_picture_id}: {str(e)}"
        )
        raise
