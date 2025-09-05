from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_session
from api.core.logging import get_logger
from api.core.security import get_current_user
from api.src.users.models import User
from api.src.users.schemas import (
    LoginData,
    LoginResponse,
    Token,
    UserCreate,
    UserResponse,
)
from api.src.users.service import UserService

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, session: AsyncSession = Depends(get_session)) -> UserResponse:
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
    return {"user": UserResponse.model_validate(user), "token": token}


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)) -> UserResponse:
    """Get current authenticated user."""
    logger.debug(f"User authenticated: {user.email}")
    return user


@router.get("/tenants", response_model=list[UserResponse])
async def get_tenants_for_owner(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[UserResponse]:
    """Get all tenant users who have leases in current user's properties."""
    logger.debug(f"Getting tenants for owner user_id={current_user.id}")

    # Only admin and owners can view tenants
    if current_user.role not in ["admin", "owner"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    # For admin, get all tenants; for owner, get only tenants in their properties
    if current_user.role == "admin":
        tenants = await UserService(session).get_all_tenants_with_status()
    else:
        tenants = await UserService(session).get_tenants_for_owner(current_user.id)

    return [UserResponse.model_validate(tenant) for tenant in tenants]


@router.get("/leases", response_model=list[dict])
async def get_leases_for_owner(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    """Get all leases in current user's properties."""
    logger.debug(f"Getting leases for owner user_id={current_user.id}")

    # Only admin and owners can view leases
    if current_user.role not in ["admin", "owner"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    # For admin, get all leases; for owner, get only leases in their properties
    if current_user.role == "admin":
        leases = await UserService(session).get_all_leases_with_details()
    else:
        leases = await UserService(session).get_leases_for_owner(current_user.id)

    return leases
