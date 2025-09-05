from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import AlreadyExistsException, NotFoundException
from api.core.logging import get_logger
from api.core.security import get_password_hash
from api.src.enums import EnumUserRoles
from api.src.leases.models import Lease
from api.src.properties.models import Property
from api.src.units.models import Unit
from api.src.users.models import User
from api.src.users.schemas import UserCreate

logger = get_logger(__name__)


class UserRepository:
    """Repository for handling user database operations."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_data: UserCreate) -> User:
        """Create a new user.

        Args:
            user_data: User creation data

        Returns:
            User: Created user

        Raises:
            AlreadyExistsException: If user with same email already exists
        """
        # Check if user exists
        existing_user = await self.get_by_email(user_data.email)
        if existing_user:
            raise AlreadyExistsException("Email already registered")

        # Create user
        user = User(email=user_data.email, hashed_password=get_password_hash(user_data.password), role=user_data.role)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        logger.info(f"Created user: {user.email}")
        return user

    async def get_by_id(self, user_id: int) -> User:
        """Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User: Found user

        Raises:
            NotFoundException: If user not found
        """
        query = select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise NotFoundException("User not found")

        return user

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email.

        Args:
            email: User email

        Returns:
            Optional[User]: Found user or None if not found
        """
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all_tenants_with_status(self) -> list[User]:
        """Get all tenant users with their lease status and current location.

        Returns:
            List[User]: List of tenant users with status and location
        """

        # Subquery to check if user has any active leases
        active_lease_subquery = (
            select(func.count(Lease.id)).where(Lease.tenant_id == User.id, Lease.is_active == True).scalar_subquery()
        )

        # Main query to get all tenants
        query = select(User).where(User.role == EnumUserRoles.TENANT).order_by(User.email)

        result = await self.session.execute(query)
        users = result.scalars().all()

        # Add status and location to each user
        for user in users:
            # Check for active leases and get current location
            active_lease_query = (
                select(Property.address)
                .join(Unit, Property.id == Unit.property_id)
                .join(Lease, Unit.id == Lease.unit_id)
                .where(Lease.tenant_id == user.id, Lease.is_active == True)
                .order_by(Lease.start_date.desc())  # Get most recent active lease
                .limit(1)
            )

            active_lease_result = await self.session.execute(active_lease_query)
            current_address = active_lease_result.scalar_one_or_none()

            # Count active leases
            active_leases_count = await self.session.execute(
                select(func.count(Lease.id)).where(Lease.tenant_id == user.id, Lease.is_active == True)
            )
            count = active_leases_count.scalar()

            user.status = "active" if count > 0 else "inactive"
            user.location = current_address

        return list(users)

    async def get_tenants_for_owner(self, owner_id: int) -> list[User]:
        """Get all tenant users who have leases in properties owned by the given owner.

        Args:
            owner_id: ID of the property owner

        Returns:
            List[User]: List of tenant users with their lease status and current location
        """

        # Query to get all tenants who have leases in units belonging to properties owned by owner_id
        query = (
            select(User)
            .join(Lease, User.id == Lease.tenant_id)
            .join(Unit, Lease.unit_id == Unit.id)
            .join(Property, Unit.property_id == Property.id)
            .where(User.role == EnumUserRoles.TENANT, Property.owner_id == owner_id)
            .distinct()
            .order_by(User.email)
        )

        result = await self.session.execute(query)
        users = result.scalars().all()

        # Add status and location to each user
        for user in users:
            # Get current location from most recent active lease in this owner's properties
            current_location_query = (
                select(Property.address)
                .join(Unit, Property.id == Unit.property_id)
                .join(Lease, Unit.id == Lease.unit_id)
                .where(Lease.tenant_id == user.id, Lease.is_active == True, Property.owner_id == owner_id)
                .order_by(Lease.start_date.desc())  # Get most recent active lease
                .limit(1)
            )

            current_location_result = await self.session.execute(current_location_query)
            current_address = current_location_result.scalar_one_or_none()

            # Count active leases in this owner's properties
            active_leases_count = await self.session.execute(
                select(func.count(Lease.id))
                .join(Unit, Lease.unit_id == Unit.id)
                .join(Property, Unit.property_id == Property.id)
                .where(Lease.tenant_id == user.id, Lease.is_active == True, Property.owner_id == owner_id)
            )
            count = active_leases_count.scalar()

            user.status = "active" if count > 0 else "inactive"
            user.location = current_address

        return list(users)

    async def get_all_leases_with_details(self) -> list[dict]:
        """Get all leases with detailed information including tenant, unit, and property details.

        Returns:
            List[dict]: List of leases with detailed information
        """
        from api.src.leases.models import Lease
        from api.src.properties.models import Property
        from api.src.units.models import Unit

        # Query to get all leases with related information
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

        # Convert to list of dictionaries
        return [
            {
                "id": lease.id,
                "unit_id": lease.unit_id,
                "tenant_id": lease.tenant_id,
                "start_date": lease.start_date.isoformat() if lease.start_date else None,
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
        """Get all leases in properties owned by the given owner.

        Args:
            owner_id: ID of the property owner

        Returns:
            List[dict]: List of leases with detailed information
        """
        from api.src.leases.models import Lease
        from api.src.properties.models import Property
        from api.src.units.models import Unit

        # Query to get all leases in properties owned by owner_id
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

        # Convert to list of dictionaries
        return [
            {
                "id": lease.id,
                "unit_id": lease.unit_id,
                "tenant_id": lease.tenant_id,
                "start_date": lease.start_date.isoformat() if lease.start_date else None,
                "end_date": lease.end_date.isoformat() if lease.end_date else None,
                "is_active": lease.is_active,
                "tenant_email": lease.tenant_email,
                "unit_name": lease.unit_name,
                "property_title": lease.property_title,
                "property_address": lease.property_address,
            }
            for lease in leases
        ]
