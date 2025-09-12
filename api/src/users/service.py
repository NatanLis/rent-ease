from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.config import settings
from api.core.exceptions import UnauthorizedException
from api.core.logging import get_logger
from api.core.security import create_access_token, verify_password
from api.src.enums import EnumUserRoles
from api.src.users.models import User
from api.src.users.repository import UserRepository
from api.src.users.schemas import (
    LoginData,
    TenantCreate,
    Token,
    UserCreate,
    UserUpdate,
)

logger = get_logger(__name__)


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = UserRepository(session)

    async def create_user(self, user_data: UserCreate) -> User:
        return await self.repository.create(user_data)

    async def create_tenant(self, tenant_data: TenantCreate) -> User:
        user_data = UserCreate(
            first_name=tenant_data.first_name,
            last_name=tenant_data.last_name,
            email=tenant_data.email,
            username=tenant_data.email,
            password=tenant_data.password,
            role=EnumUserRoles.TENANT,
        )
        return await self.repository.create(user_data)

    async def authenticate(self, login_data: LoginData) -> Token:
        user = await self.repository.get_by_email(login_data.email)
        if not user or not verify_password(
            login_data.password, str(user.hashed_password)
        ):
            raise UnauthorizedException(detail="Incorrect email or password")

        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.JWT_EXPIRATION),
        )

        logger.info(f"User authenticated: {user.email}")
        return Token(access_token=access_token)

    async def get_user(self, user_id: int) -> User:
        return await self.repository.get_by_id(user_id)

    async def get_user_by_email(self, email: str) -> User:
        return await self.repository.get_by_email(email)

    async def get_user_by_username(self, username: str) -> User:
        return await self.repository.get_by_username(username)

    async def get_all_users(self, role: str = None) -> list[User]:
        return await self.repository.get_all_users(role)

    async def get_all_tenants_with_status(self) -> list[User]:
        return await self.repository.get_all_tenants_with_status()

    async def get_tenants_for_owner(self, owner_id: int) -> list[User]:
        return await self.repository.get_tenants_for_owner(owner_id)

    async def get_all_leases_with_details(self) -> list[dict]:
        return await self.repository.get_all_leases_with_details()

    async def get_leases_for_owner(self, owner_id: int) -> list[dict]:
        return await self.repository.get_leases_for_owner(owner_id)

    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        return await self.repository.update(user_id, user_data)

    async def delete_user(self, user_id: int) -> None:
        await self.repository.delete(user_id)
