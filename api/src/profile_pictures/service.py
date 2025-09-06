from typing import Optional

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.logging import get_logger
from .models import ProfilePicture
from .schemas import ProfilePictureCreate, ProfilePictureDownload

logger = get_logger(__name__)


class ProfilePictureService:
    """Service for managing profile pictures."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_profile_picture(
        self, user_id: int, profile_picture_data: ProfilePictureCreate
    ) -> ProfilePicture:
        """Create a new profile picture for a user."""
        logger.debug(f"Creating profile picture for user {user_id}")
        
        # Delete existing profile picture if it exists
        await self.delete_profile_picture_by_user_id(user_id)
        
        # Create new profile picture
        profile_picture = ProfilePicture(
            user_id=user_id,
            filename=profile_picture_data.filename,
            mimetype=profile_picture_data.mimetype,
            size=profile_picture_data.size,
            data=profile_picture_data.data
        )
        
        self.session.add(profile_picture)
        await self.session.commit()
        await self.session.refresh(profile_picture)
        
        logger.info(f"Created profile picture {profile_picture.id} for user {user_id}")
        return profile_picture

    async def get_profile_picture(self, profile_picture_id: int) -> Optional[ProfilePicture]:
        """Get profile picture by ID."""
        logger.debug(f"Fetching profile picture {profile_picture_id}")
        
        result = await self.session.execute(
            select(ProfilePicture).where(ProfilePicture.id == profile_picture_id)
        )
        return result.scalar_one_or_none()

    async def get_profile_picture_by_user_id(self, user_id: int) -> Optional[ProfilePicture]:
        """Get profile picture by user ID."""
        logger.debug(f"Fetching profile picture for user {user_id}")
        
        result = await self.session.execute(
            select(ProfilePicture).where(ProfilePicture.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_profile_picture_for_download(
        self, profile_picture_id: int
    ) -> Optional[ProfilePictureDownload]:
        """Get profile picture data for download."""
        logger.debug(f"Fetching profile picture {profile_picture_id} for download")
        
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
            data=profile_picture.data
        )

    async def delete_profile_picture(self, profile_picture_id: int) -> bool:
        """Delete profile picture by ID."""
        logger.debug(f"Deleting profile picture {profile_picture_id}")
        
        result = await self.session.execute(
            delete(ProfilePicture).where(ProfilePicture.id == profile_picture_id)
        )
        await self.session.commit()
        
        deleted = result.rowcount > 0
        if deleted:
            logger.info(f"Deleted profile picture {profile_picture_id}")
        else:
            logger.warning(f"Profile picture {profile_picture_id} not found for deletion")
            
        return deleted

    async def delete_profile_picture_by_user_id(self, user_id: int) -> bool:
        """Delete profile picture by user ID."""
        logger.debug(f"Deleting profile picture for user {user_id}")
        
        result = await self.session.execute(
            delete(ProfilePicture).where(ProfilePicture.user_id == user_id)
        )
        await self.session.commit()
        
        deleted = result.rowcount > 0
        if deleted:
            logger.info(f"Deleted profile picture for user {user_id}")
        else:
            logger.debug(f"No profile picture found for user {user_id}")
            
        return deleted
