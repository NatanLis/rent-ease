from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.core.logging import get_logger
from api.core.security import get_current_user
from api.src.users.models import User
from api.src.users.schemas import LoginData, Token, UserCreate, UserResponse, LoginResponse
from api.src.users.service import UserService

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    user_data: UserCreate, session: AsyncSession = Depends(get_session)
) -> UserResponse:
    """Register a new user."""
    logger.debug(f"Registering user: {user_data.email}")
    return await UserService(session).create_user(user_data)


@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session),
) -> LoginResponse:
    """Authenticate user and return token."""
    login_data = LoginData(email=form_data.username, password=form_data.password)
    logger.debug(f"Login attempt: {login_data.email}")
    token: Token = await UserService(session).authenticate(login_data)
    user: User = await UserService(session).get_user_by_email(login_data.email)
    return {
        "user": UserResponse.model_validate(user),
        "token": token
    }

@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)) -> UserResponse:
    """Get current authenticated user."""
    logger.debug(f"User authenticated: {user.email}")
    return user




# Add a new router for general user operations
users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get("/", response_model=list[UserResponse])
async def get_all_users(
    role: Optional[str] = Query(None, description="Filter by role (ADMIN, OWNER, TENANT)"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[UserResponse]:
    """Get all users, optionally filtered by role."""
    logger.debug(f"Getting all users with role filter: {role}")
    logger.debug(f"Current user: {current_user.email}, role: {current_user.role}")
    
    # Only admin and owners can view users
    if current_user.role not in ["admin", "owner"]:
        logger.warning(f"Access denied for user {current_user.email} with role {current_user.role}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # For admin, get all users; for owner, get only tenants in their properties
    if current_user.role == "admin":
        users = await UserService(session).get_all_users(role)
    else:
        # For owner, only get tenants who have leases in their properties
        if role and role.lower() != "tenant":
            # Owner can only see tenants, not other roles
            users = []
        else:
            users = await UserService(session).get_tenants_for_owner(current_user.id)
    
    # Transform users to include avatar_url
    result = []
    for user in users:
        user_dict = UserResponse.model_validate(user).model_dump()
        # Only set avatar_url if user has a profile picture
        if user.profile_picture_id:
            user_dict['avatar_url'] = f"/api/profile-pictures/{user.profile_picture_id}/download"
        # If no profile picture, avatar_url will be None by default
        result.append(UserResponse(**user_dict))
    
    return result



