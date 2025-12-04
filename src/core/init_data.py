"""Initialize default data on application startup."""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .config import settings
from ..schemas.user import UserCreate
from ..services.user_service import UserService
from ..repositories.user_repository import UserRepository
from ..models.user import User, Role, user_roles
from ..services.exceptions import AlreadyExistsError

logger = logging.getLogger(__name__)


async def create_admin_role(session: AsyncSession) -> Role:
    """Create admin role if not exists."""
    result = await session.execute(
        select(Role).where(Role.name == "admin")
    )
    admin_role = result.scalar_one_or_none()
    
    if not admin_role:
        admin_role = Role(name="admin")
        session.add(admin_role)
        await session.commit()
        await session.refresh(admin_role)
        logger.info("Admin role created")
    else:
        logger.info("Admin role already exists")
    
    return admin_role


async def assign_admin_role_to_user(user: User, admin_role: Role, session: AsyncSession) -> None:
    """Assign admin role to user if not already assigned."""
    # Refresh user to get roles
    await session.refresh(user, ['roles'])
    
    # Check if user already has admin role
    if admin_role in user.roles:
        logger.info(f"User '{user.username}' already has admin role")
        return
    
    # Assign admin role
    user.roles.append(admin_role)
    await session.commit()
    logger.info(f"Admin role assigned to user '{user.username}'")


async def create_default_admin(session: AsyncSession) -> None:
    """Create default admin user if not exists."""
    user_repo = UserRepository()
    user_service = UserService(user_repo)
    
    try:
        # Create admin role first
        admin_role = await create_admin_role(session)
        
        # Check if admin already exists
        existing_admin = await user_repo.get_by_username(
            settings.ADMIN_USERNAME,
            session
        )
        
        if existing_admin:
            logger.info(f"Admin user '{settings.ADMIN_USERNAME}' already exists")
            # Ensure admin role is assigned
            await assign_admin_role_to_user(existing_admin, admin_role, session)
            return
        
        # Create admin user
        admin_data = UserCreate(
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            password=settings.ADMIN_PASSWORD,
            is_active=True
        )
        
        admin_user_read = await user_service.create(admin_data, session)
        
        # Get the actual User model instance to assign role
        admin_user = await user_repo.get_by_id(admin_user_read.id, session)
        if admin_user:
            await assign_admin_role_to_user(admin_user, admin_role, session)
        
        logger.info(
            f"Default admin user created: "
            f"username='{admin_user_read.username}', "
            f"email='{admin_user_read.email}'"
        )
        
    except AlreadyExistsError:
        logger.info(f"Admin user '{settings.ADMIN_USERNAME}' already exists")
        # Ensure admin role is assigned even if user exists
        existing_admin = await user_repo.get_by_username(
            settings.ADMIN_USERNAME,
            session
        )
        if existing_admin:
            admin_role = await create_admin_role(session)
            await assign_admin_role_to_user(existing_admin, admin_role, session)
    except Exception as e:
        logger.error(f"Failed to create admin user: {e}")
        raise


async def initialize_default_data(session: AsyncSession) -> None:
    """Initialize all default data."""
    logger.info("Initializing default data...")
    await create_default_admin(session)
    logger.info("Default data initialization complete")
