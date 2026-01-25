"""Authentication endpoints."""

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from ..core.dependencies import UsersDBSession, UserSvc
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
async def register(user_data: UserCreate, user_service: UserSvc, db: UsersDBSession):
    """Register a new user."""
    user = await user_service.create(user_data, db)
    return Response(success=True, message="User registered successfully", data=user)


@router.post(
    "/login",
    response_model=Response[TokenResponse],
    summary="Login user",
    description="Authenticate user and receive JWT tokens",
)
async def login(credentials: LoginRequest, user_service: UserSvc, db: UsersDBSession):
    """Authenticate user and return JWT tokens."""
    auth_result = await user_service.authenticate(credentials.username, credentials.password, db)

    token_response = TokenResponse(**auth_result)

    return Response(success=True, message="Login successful", data=token_response)


@router.get(
    "/me",
    response_model=Response[UserRead],
    summary="Get current user",
    description="Get current authenticated user information",
)
async def get_current_user(
    # TODO: Add JWT authentication dependency
    user_service: UserSvc,
    db: UsersDBSession,
):
    """Get current user information."""
    # Placeholder - will be implemented with JWT auth middleware
    return Response(success=True, message="Current user retrieved", data=None)
