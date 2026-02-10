"""Initialize default data on application startup."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import Role, User
from ..repositories.user_repository import UserRepository
from ..schemas.user import UserCreate
from ..services.exceptions import AlreadyExistsError
from ..services.user_service import UserService
from .config import settings
from .logging_config import get_logger

logger = get_logger(__name__)


async def create_admin_role(session: AsyncSession) -> Role:
    """Create admin role if not exists."""
    result = await session.execute(select(Role).where(Role.name == "admin"))
    admin_role = result.scalar_one_or_none()

    if not admin_role:
        admin_role = Role(name="admin")
        session.add(admin_role)
        await session.flush()
        await session.refresh(admin_role)
        logger.info("admin_role_created")
    else:
        logger.info("admin_role_already_exists")

    return admin_role


async def assign_admin_role_to_user(
    user: User, admin_role: Role, session: AsyncSession
) -> None:
    """Assign admin role to user if not already assigned."""
    await session.refresh(user, ["roles"])

    if admin_role in user.roles:
        logger.info("user_already_has_admin_role", username=user.username)
        return

    user.roles.append(admin_role)
    await session.flush()
    logger.info("admin_role_assigned", username=user.username)


async def create_default_admin(session: AsyncSession) -> None:
    """Create default admin user if not exists."""
    user_repo = UserRepository()
    user_service = UserService(user_repo)

    try:
        admin_role = await create_admin_role(session)

        existing_admin = await user_repo.get_by_username(
            settings.ADMIN_USERNAME, session
        )

        if existing_admin:
            logger.info("admin_user_already_exists", username=settings.ADMIN_USERNAME)
            await assign_admin_role_to_user(existing_admin, admin_role, session)
            return

        admin_data = UserCreate(
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            password=settings.ADMIN_PASSWORD,
            is_active=True,
        )

        admin_user_read = await user_service.create(admin_data, session)

        admin_user = await user_repo.get_by_id(admin_user_read.id, session)
        if admin_user:
            await assign_admin_role_to_user(admin_user, admin_role, session)

        logger.info(
            "default_admin_created",
            username=admin_user_read.username,
            email=admin_user_read.email,
        )

    except AlreadyExistsError:
        logger.info("admin_user_already_exists", username=settings.ADMIN_USERNAME)
        existing_admin = await user_repo.get_by_username(
            settings.ADMIN_USERNAME, session
        )
        if existing_admin:
            admin_role = await create_admin_role(session)
            await assign_admin_role_to_user(existing_admin, admin_role, session)
    except Exception:
        logger.exception("failed_to_create_admin_user")
        raise


async def initialize_default_data(session: AsyncSession) -> None:
    """Initialize all default data."""
    logger.info("initializing_default_data")
    await create_default_admin(session)
    logger.info("default_data_initialization_complete")
