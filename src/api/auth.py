"""Authentication endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel, Field

from ..core.dependencies import (
    AuthSvc,
    RegistrationAllowed,
    UsersDBSession,
    UserSvc,
    get_current_user,
    oauth2_scheme,
)
from ..core.rate_limit import limiter
from ..core.security import (
    TokenValidationError,
    verify_access_token,
    verify_refresh_token,
)
from ..core.token_store import blacklist_access_jti, blacklist_refresh_token
from ..schemas.user import UserCreate, UserRead
from ..services.exceptions import AuthenticationError
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
@limiter.limit("3/minute")
async def register(
    request: Request,
    user_data: UserCreate,
    user_service: UserSvc,
    db: UsersDBSession,
    _: RegistrationAllowed,
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
@limiter.limit("5/minute")
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


class RefreshRequest(BaseModel):
    """Refresh token request."""

    refresh_token: str = Field(..., description="JWT refresh token")


@router.post(
    "/refresh",
    response_model=Response[TokenResponse],
    summary="Refresh access token",
    description="Exchange a valid refresh token for a new access token",
)
@limiter.limit("20/minute")
async def refresh_access_token(
    request: Request,
    body: RefreshRequest,
    auth_service: AuthSvc,
    db: UsersDBSession,
):
    """Issue a new access token using a valid refresh token."""
    try:
        payload = verify_refresh_token(body.refresh_token)
    except TokenValidationError as exc:
        raise AuthenticationError(exc.message) from exc

    auth_result = await auth_service.refresh(
        payload, db, previous_refresh_token=body.refresh_token
    )
    return Response(
        success=True, message="Token refreshed", data=TokenResponse(**auth_result)
    )


class LogoutRequest(BaseModel):
    """Optional refresh token to also revoke on logout."""

    refresh_token: str | None = Field(
        None, description="Refresh token to invalidate alongside the access token"
    )


@router.post(
    "/logout",
    response_model=Response[dict],
    summary="Logout (revoke access + refresh tokens)",
    description=(
        "Revokes the current access token by adding its JTI to the blacklist. "
        "If a refresh_token is provided, it is also blacklisted."
    ),
)
async def logout(
    body: LogoutRequest | None = None,
    token: str = Depends(oauth2_scheme),
    _current_user: Annotated[UserRead, Depends(get_current_user)] = None,  # type: ignore[assignment]
):
    """Revoke the caller's current access token and (optionally) refresh token."""
    try:
        payload = verify_access_token(token)
    except TokenValidationError as exc:
        raise AuthenticationError(exc.message) from exc

    jti = payload.get("jti")
    exp = payload.get("exp")
    if jti:
        await blacklist_access_jti(jti, exp)

    if body and body.refresh_token:
        try:
            refresh_payload = verify_refresh_token(body.refresh_token)
            refresh_exp = refresh_payload.get("exp")
            if isinstance(refresh_exp, int):
                await blacklist_refresh_token(body.refresh_token, refresh_exp)
        except TokenValidationError:
            # Best-effort: a malformed/expired refresh token doesn't fail logout.
            pass

    return Response(success=True, message="Logged out", data={})


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
