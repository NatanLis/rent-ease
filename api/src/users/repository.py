from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import AlreadyExistsException, NotFoundException
from api.core.logging import get_logger
from api.core.security import get_password_hash
from api.src.enums import EnumUserRoles
from api.src.enums.utils import Status
from api.src.leases.models import Lease
from api.src.properties.models import Property
from api.src.units.models import Unit
from api.src.users.models import User
from api.src.users.schemas import UserCreate, UserUpdate

logger = get_logger(__name__)


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_data: UserCreate) -> User:
        existing_user = await self.get_by_email(user_data.email)
        if existing_user:
            raise AlreadyExistsException("Email already registered")

        user = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            username=user_data.username,
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            role=user_data.role,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        logger.info(f"Created user: {user.email}")
        return user

    async def get_by_id(self, user_id: int) -> User:
        query = select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundException("User not found")

        return user

    async def get_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        query = select(User).where(User.username == username)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_users(self, role: str = None) -> list[User]:
        query = select(User)

        if role and role.upper() in EnumUserRoles.__members__:
            role_enum = EnumUserRoles[role.upper()]
            query = query.where(User.role == role_enum)

        query = query.order_by(User.email)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_all_tenants_with_status(self) -> list[User]:
        query = (
            select(User).where(User.role == EnumUserRoles.TENANT).order_by(User.email)
        )

        result = await self.session.execute(query)
        users = result.scalars().all()

        for user in users:
            active_lease_query = (
                select(Property.address)
                .join(Unit, Property.id == Unit.property_id)
                .join(Lease, Unit.id == Lease.unit_id)
                .where(
                    Lease.tenant_id == user.id,
                    Lease.is_active == True,  # noqa: E712
                )
                .order_by(Lease.start_date.desc())
                .limit(1)
            )

            active_lease_result = await self.session.execute(active_lease_query)
            current_address = active_lease_result.scalar_one_or_none()

            active_leases_count = await self.session.execute(
                select(func.count(Lease.id)).where(
                    Lease.tenant_id == user.id,
                    Lease.is_active == True,  # noqa: E712
                )
            )
            count = active_leases_count.scalar()

            user.status = Status.ACTIVE if count > 0 else Status.INACTIVE
            user.location = current_address

        return list(users)

    async def get_tenants_for_owner(self, owner_id: int) -> list[User]:
        query = (
            select(User)
            .join(Lease, User.id == Lease.tenant_id)
            .join(Unit, Lease.unit_id == Unit.id)
            .join(Property, Unit.property_id == Property.id)
            .where(
                User.role == EnumUserRoles.TENANT,
                Property.owner_id == owner_id,
            )
            .distinct()
            .order_by(User.email)
        )

        result = await self.session.execute(query)
        users = result.scalars().all()

        for user in users:
            current_location_query = (
                select(Property.address)
                .join(Unit, Property.id == Unit.property_id)
                .join(Lease, Unit.id == Lease.unit_id)
                .where(
                    Lease.tenant_id == user.id,
                    Lease.is_active == True,  # noqa: E712
                    Property.owner_id == owner_id,
                )
                .order_by(Lease.start_date.desc())
                .limit(1)
            )

            current_location_result = await self.session.execute(
                current_location_query
            )
            current_address = current_location_result.scalar_one_or_none()

            active_leases_count = await self.session.execute(
                select(func.count(Lease.id))
                .join(Unit, Lease.unit_id == Unit.id)
                .join(Property, Unit.property_id == Property.id)
                .where(
                    Lease.tenant_id == user.id,
                    Lease.is_active == True,  # noqa: E712
                    Property.owner_id == owner_id,
                )
            )
            count = active_leases_count.scalar()

            user.status = Status.ACTIVE if count > 0 else Status.INACTIVE
            user.location = current_address

        return list(users)

    async def get_all_leases_with_details(self) -> list[dict]:
        query = (
            select(
                Lease.id,
                Lease.unit_id,
                Lease.tenant_id,
                Lease.start_date,
                Lease.end_date,
                Lease.is_active,
                User.email.label("tenant_email"),
                Unit.name.label("unit_name"),
                Property.title.label("property_title"),
                Property.address.label("property_address"),
            )
            .join(User, Lease.tenant_id == User.id)
            .join(Unit, Lease.unit_id == Unit.id)
            .join(Property, Unit.property_id == Property.id)
            .order_by(Lease.start_date.desc())
        )

        result = await self.session.execute(query)
        leases = result.fetchall()

        return [
            {
                "id": lease.id,
                "unit_id": lease.unit_id,
                "tenant_id": lease.tenant_id,
                "start_date": lease.start_date.isoformat()
                if lease.start_date
                else None,
                "end_date": lease.end_date.isoformat() if lease.end_date else None,
                "is_active": lease.is_active,
                "tenant_email": lease.tenant_email,
                "unit_name": lease.unit_name,
                "property_title": lease.property_title,
                "property_address": lease.property_address,
            }
            for lease in leases
        ]

    async def get_leases_for_owner(self, owner_id: int) -> list[dict]:
        query = (
            select(
                Lease.id,
                Lease.unit_id,
                Lease.tenant_id,
                Lease.start_date,
                Lease.end_date,
                Lease.is_active,
                User.email.label("tenant_email"),
                Unit.name.label("unit_name"),
                Property.title.label("property_title"),
                Property.address.label("property_address"),
            )
            .join(User, Lease.tenant_id == User.id)
            .join(Unit, Lease.unit_id == Unit.id)
            .join(Property, Unit.property_id == Property.id)
            .where(Property.owner_id == owner_id)
            .order_by(Lease.start_date.desc())
        )

        result = await self.session.execute(query)
        leases = result.fetchall()

        return [
            {
                "id": lease.id,
                "unit_id": lease.unit_id,
                "tenant_id": lease.tenant_id,
                "start_date": lease.start_date.isoformat()
                if lease.start_date
                else None,
                "end_date": lease.end_date.isoformat() if lease.end_date else None,
                "is_active": lease.is_active,
                "tenant_email": lease.tenant_email,
                "unit_name": lease.unit_name,
                "property_title": lease.property_title,
                "property_address": lease.property_address,
            }
            for lease in leases
        ]

    async def update(self, user_id: int, user_data: UserUpdate) -> User:
        user = await self.get_by_id(user_id)
        update_data = user_data.model_dump(exclude_unset=True)
        if not update_data:
            return user

        for field, value in update_data.items():
            setattr(user, field, value)

        await self.session.commit()
        await self.session.refresh(user)

        logger.info(f"Updated user: {user.email}")
        return user

    async def delete(self, user_id: int) -> None:
        user = await self.get_by_id(user_id)

        await self.session.delete(user)
        await self.session.commit()

        logger.info(f"Deleted user: {user.email}")
