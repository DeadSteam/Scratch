"""Authentication endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel, Field

from ..core.dependencies import AuthSvc, UsersDBSession, UserSvc, get_current_user
from ..core.rate_limit import limiter
from ..schemas.user import UserCreate, UserRead
from .responses import Response

router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    """Login request model."""

    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class TokenResponse(BaseModel):
    """Token response model."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    user: UserRead = Field(..., description="User information")


@router.post(
    "/register",
    response_model=Response[UserRead],
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create a new user account with username, email, and password",
)
@limiter.limit("5/minute")
async def register(
    request: Request, user_data: UserCreate, user_service: UserSvc, db: UsersDBSession
):
    """Register a new user."""
    user = await user_service.create(user_data, db)
    return Response(success=True, message="User registered successfully", data=user)


@router.post(
    "/login",
    response_model=Response[TokenResponse],
    summary="Login user",
    description="Authenticate user and receive JWT tokens",
)
@limiter.limit("10/minute")
async def login(
    request: Request,
    credentials: LoginRequest,
    auth_service: AuthSvc,
    db: UsersDBSession,
):
    """Authenticate user and return JWT tokens."""
    auth_result = await auth_service.authenticate(
        credentials.username, credentials.password, db
    )
    token_response = TokenResponse(**auth_result)
    return Response(success=True, message="Login successful", data=token_response)


@router.get(
    "/me",
    response_model=Response[UserRead],
    summary="Get current user",
    description="Get current authenticated user information",
)
async def get_current_user_info(
    current_user: Annotated[UserRead, Depends(get_current_user)],
):
    """Get current user information."""
    return Response(success=True, message="Current user retrieved", data=current_user)
