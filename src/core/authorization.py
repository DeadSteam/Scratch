"""Resource-level authorization helpers."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.experiment import Experiment
from ..models.image import ExperimentImage
from ..schemas.user import UserRead
from ..services.exceptions import AuthorizationError, NotFoundError


def is_admin(user: UserRead) -> bool:
    """Return True if the user has the admin role."""
    return any(role.name == "admin" for role in user.roles)


def ensure_same_user_or_admin(user: UserRead, owner_id: UUID) -> None:
    """Allow access when user is admin or owns the resource."""
    if is_admin(user):
        return
    if user.id != owner_id:
        raise AuthorizationError("Access forbidden: you do not own this resource")


async def get_experiment_owner_id(experiment_id: UUID, session: AsyncSession) -> UUID:
    """Load experiment owner user_id or raise NotFoundError."""
    result = await session.execute(
        select(Experiment.user_id).where(Experiment.id == experiment_id)
    )
    owner_id = result.scalar_one_or_none()
    if owner_id is None:
        raise NotFoundError("Experiment", experiment_id)
    return owner_id


async def ensure_experiment_access(
    experiment_id: UUID, user: UserRead, session: AsyncSession
) -> None:
    """Verify the user may access the experiment."""
    owner_id = await get_experiment_owner_id(experiment_id, session)
    ensure_same_user_or_admin(user, owner_id)


async def ensure_image_access(
    image_id: UUID, user: UserRead, session: AsyncSession
) -> None:
    """Verify the user may access the image via its parent experiment."""
    result = await session.execute(
        select(ExperimentImage.experiment_id).where(ExperimentImage.id == image_id)
    )
    experiment_id = result.scalar_one_or_none()
    if experiment_id is None:
        raise NotFoundError("ExperimentImage", image_id)
    await ensure_experiment_access(experiment_id, user, session)
