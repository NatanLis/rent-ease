from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.config import settings
from api.core.exceptions import UnauthorizedException
from api.core.logging import get_logger
from api.core.security import create_access_token, verify_password
from api.src.users.models import User
from api.src.users.repository import UserRepository
from api.src.users.schemas import LoginData, Token, UserCreate, UserUpdate

logger = get_logger(__name__)


class UserService:
    """Service for handling user business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = UserRepository(session)

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        return await self.repository.create(user_data)

    async def authenticate(self, login_data: LoginData) -> Token:
        """Authenticate user and return token."""
        # Get user
        user = await self.repository.get_by_email(login_data.email)

        # Verify credentials
        if not user or not verify_password(
            login_data.password, str(user.hashed_password)
        ):
            raise UnauthorizedException(detail="Incorrect email or password")

        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.JWT_EXPIRATION),
        )

        logger.info(f"User authenticated: {user.email}")
        return Token(access_token=access_token)

    async def get_user(self, user_id: int) -> User:
        """Get user by ID."""
        return await self.repository.get_by_id(user_id)

    async def get_user_by_email(self, email: str) -> User:
        """Get user by email."""
        return await self.repository.get_by_email(email)

    async def get_all_users(self, role: str = None) -> list[User]:
        """Get all users, optionally filtered by role."""
        return await self.repository.get_all_users(role)

    async def get_all_tenants_with_status(self) -> list[User]:
        """Get all tenant users with their lease status."""
        return await self.repository.get_all_tenants_with_status()

    async def get_tenants_for_owner(self, owner_id: int) -> list[User]:
        """Get all tenant users who have leases in properties owned by the given owner."""
        return await self.repository.get_tenants_for_owner(owner_id)

    async def get_all_leases_with_details(self) -> list[dict]:
        """Get all leases with detailed information."""
        return await self.repository.get_all_leases_with_details()

    async def get_leases_for_owner(self, owner_id: int) -> list[dict]:
        """Get all leases in properties owned by the given owner."""
        return await self.repository.get_leases_for_owner(owner_id)

    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Update user by ID."""
        return await self.repository.update(user_id, user_data)

    async def delete_user(self, user_id: int) -> None:
        """Delete user by ID."""
        await self.repository.delete(user_id)