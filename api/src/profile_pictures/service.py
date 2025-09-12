from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.logging import get_logger
from api.src.profile_pictures.models import ProfilePicture
from api.src.profile_pictures.schemas import (
    ProfilePictureCreate,
    ProfilePictureDownload,
)

logger = get_logger(__name__)


class ProfilePictureService:
    """Service for managing profile pictures."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_profile_picture(
        self,
        user_id: int,
        profile_picture_data: ProfilePictureCreate,
    ) -> ProfilePicture:
        await self.delete_profile_picture_by_user_id(user_id)

        profile_picture = ProfilePicture(
            user_id=user_id,
            filename=profile_picture_data.filename,
            mimetype=profile_picture_data.mimetype,
            size=profile_picture_data.size,
            data=profile_picture_data.data,
        )

        self.session.add(profile_picture)
        await self.session.commit()
        await self.session.refresh(profile_picture)

        return profile_picture

    async def get_profile_picture(
        self, profile_picture_id: int
    ) -> Optional[ProfilePicture]:
        result = await self.session.execute(
            select(ProfilePicture).where(ProfilePicture.id == profile_picture_id)
        )
        return result.scalar_one_or_none()

    async def get_profile_picture_by_user_id(
        self,
        user_id: int,
    ) -> Optional[ProfilePicture]:
        logger.debug(f"Fetching profile picture for user {user_id}")

        result = await self.session.execute(
            select(ProfilePicture).where(ProfilePicture.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_profile_picture_for_download(
        self,
        profile_picture_id: int,
    ) -> Optional[ProfilePictureDownload]:
        result = await self.session.execute(
            select(ProfilePicture).where(ProfilePicture.id == profile_picture_id)
        )
        profile_picture = result.scalar_one_or_none()

        if not profile_picture:
            return None

        return ProfilePictureDownload(
            id=profile_picture.id,
            filename=profile_picture.filename,
            mimetype=profile_picture.mimetype,
            data=profile_picture.data,
        )

    async def delete_profile_picture(
        self,
        profile_picture_id: int,
    ) -> bool:
        result = await self.session.execute(
            delete(ProfilePicture).where(ProfilePicture.id == profile_picture_id)
        )
        await self.session.commit()

        return bool(result.rowcount)

    async def delete_profile_picture_by_user_id(
        self,
        user_id: int,
    ) -> bool:
        result = await self.session.execute(
            delete(ProfilePicture).where(ProfilePicture.user_id == user_id)
        )
        await self.session.commit()
        return bool(result.rowcount)
