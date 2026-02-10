"""User management endpoints."""

from uuid import UUID

from fastapi import APIRouter, Query, status

from ..core.dependencies import CurrentAdmin, UsersDBSession, UserSvc
from ..schemas.user import UserCreate, UserRead, UserUpdate
from .responses import PaginatedResponse, Response

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/",
    response_model=PaginatedResponse[UserRead],
    summary="List users",
    description="Get paginated list of all users",
)
async def list_users(
    user_service: UserSvc,
    db: UsersDBSession,
    admin: CurrentAdmin,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return"),
):
    """Get list of users with pagination."""
    users = await user_service.get_all(db, skip, limit)
    total = await user_service.count(db)

    return PaginatedResponse(
        success=True,
        data=users,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + len(users)) < total,
    )


@router.get(
    "/active",
    response_model=PaginatedResponse[UserRead],
    summary="List active users",
    description="Get paginated list of active users only",
)
async def list_active_users(
    user_service: UserSvc,
    db: UsersDBSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get list of active users."""
    users = await user_service.get_active_users(db, skip, limit)
    total = await user_service.count_active(db)

    return PaginatedResponse(
        success=True,
        data=users,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + len(users)) < total,
    )


@router.post(
    "/",
    response_model=Response[UserRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
    description="Create a new user account",
)
async def create_user(
    user_data: UserCreate, user_service: UserSvc, db: UsersDBSession, admin: CurrentAdmin
):
    """Create new user."""
    user = await user_service.create(user_data, db)
    return Response(success=True, message="User created successfully", data=user)


@router.get(
    "/{user_id}",
    response_model=Response[UserRead],
    summary="Get user by ID",
    description="Retrieve a specific user by their ID",
)
async def get_user(user_id: UUID, user_service: UserSvc, db: UsersDBSession):
    """Get user by ID."""
    user = await user_service.get_by_id(user_id, db)
    return Response(success=True, message="User retrieved successfully", data=user)


@router.get(
    "/username/{username}",
    response_model=Response[UserRead],
    summary="Get user by username",
    description="Retrieve a specific user by their username",
)
async def get_user_by_username(
    username: str, user_service: UserSvc, db: UsersDBSession
):
    """Get user by username."""
    user = await user_service.get_by_username(username, db)
    return Response(success=True, message="User retrieved successfully", data=user)


@router.put(
    "/{user_id}",
    response_model=Response[UserRead],
    summary="Update user",
    description="Update user information",
)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    user_service: UserSvc,
    db: UsersDBSession,
    admin: CurrentAdmin,
):
    """Update user information."""
    user = await user_service.update(user_id, user_data, db)
    return Response(success=True, message="User updated successfully", data=user)


@router.post(
    "/{user_id}/deactivate",
    response_model=Response[UserRead],
    summary="Deactivate user",
    description="Deactivate a user account",
)
async def deactivate_user(
    user_id: UUID, user_service: UserSvc, db: UsersDBSession, admin: CurrentAdmin
):
    """Deactivate user account."""
    user = await user_service.deactivate_user(user_id, db)
    return Response(success=True, message="User deactivated successfully", data=user)


@router.post(
    "/{user_id}/activate",
    response_model=Response[UserRead],
    summary="Activate user",
    description="Activate a user account",
)
async def activate_user(
    user_id: UUID, user_service: UserSvc, db: UsersDBSession, admin: CurrentAdmin
):
    """Activate user account."""
    user = await user_service.activate_user(user_id, db)
    return Response(success=True, message="User activated successfully", data=user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Permanently delete a user account",
)
async def delete_user(
    user_id: UUID, user_service: UserSvc, db: UsersDBSession, admin: CurrentAdmin
):
    """Delete user."""
    await user_service.delete(user_id, db)
    return None
