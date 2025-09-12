from typing import Annotated

from fastapi import APIRouter, Depends, status
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
    UserUpdate,
)
from api.src.users.service import UserService

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session),
) -> UserResponse:
    return await UserService(session).create_user(user_data)


@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session),
) -> LoginResponse:
    login_data = LoginData(email=form_data.username, password=form_data.password)
    token: Token = await UserService(session).authenticate(login_data)
    user: User = await UserService(session).get_user_by_email(login_data.email)
    return {"user": UserResponse.model_validate(user), "token": token}


@router.get("/me", response_model=UserResponse)
async def get_me(
    user: User = Depends(get_current_user),
) -> UserResponse:
    logger.debug(f"User authenticated: {user.email}")
    return user


@router.put("/me", response_model=UserResponse)
async def update_me(
    user_data: UserUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Update current user's profile"""
    logger.debug(f"Updating profile for user: {current_user.email}")
    updated_user = await UserService(session).update_user(current_user.id, user_data)
    return UserResponse.model_validate(updated_user)
