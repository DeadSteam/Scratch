"""FastAPI dependency injection configuration.

All repositories and services are wired here as Depends() providers.
Type aliases (e.g. CurrentUser, MainDBSession) keep endpoint signatures clean.
"""

from collections.abc import AsyncGenerator
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories import (
    AdviceRepository,
    CauseRepository,
    EquipmentConfigRepository,
    ExperimentImageRepository,
    ExperimentRepository,
    FilmRepository,
    SituationRepository,
    UserRepository,
)
from ..schemas.user import UserRead
from ..services import (
    EquipmentConfigService,
    ExperimentImageService,
    ExperimentService,
    FilmService,
    UserService,
)
from ..services.advice_service import AdviceService
from ..services.auth_service import AuthService
from ..services.cause_service import CauseService
from ..services.exceptions import AuthenticationError, AuthorizationError
from ..services.image_analysis_service import ImageAnalysisService
from ..services.situation_service import SituationService
from .database import get_db_session, get_knowledge_db_session, get_users_db_session
from .redis import get_redis_client
from .security import TokenValidationError, verify_token

# ---------------------------------------------------------------------------
# Auth scheme
# ---------------------------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


# ---------------------------------------------------------------------------
# Database session dependencies
# ---------------------------------------------------------------------------
async def get_main_db() -> AsyncGenerator[AsyncSession]:
    """Get main database session."""
    async for session in get_db_session():
        yield session


async def get_users_db() -> AsyncGenerator[AsyncSession]:
    """Get users database session."""
    async for session in get_users_db_session():
        yield session


async def get_knowledge_db() -> AsyncGenerator[AsyncSession]:
    """Get knowledge base database session."""
    async for session in get_knowledge_db_session():
        yield session


# ---------------------------------------------------------------------------
# Repository providers (stateless singletons)
# ---------------------------------------------------------------------------
_user_repo = UserRepository()
_experiment_repo = ExperimentRepository()
_film_repo = FilmRepository()
_config_repo = EquipmentConfigRepository()
_image_repo = ExperimentImageRepository()
_situation_repo = SituationRepository()
_cause_repo = CauseRepository()
_advice_repo = AdviceRepository()


def get_user_repository() -> UserRepository:
    return _user_repo


def get_experiment_repository() -> ExperimentRepository:
    return _experiment_repo


def get_film_repository() -> FilmRepository:
    return _film_repo


def get_equipment_config_repository() -> EquipmentConfigRepository:
    return _config_repo


def get_experiment_image_repository() -> ExperimentImageRepository:
    return _image_repo


def get_situation_repository() -> SituationRepository:
    return _situation_repo


def get_cause_repository() -> CauseRepository:
    return _cause_repo


def get_advice_repository() -> AdviceRepository:
    return _advice_repo


# ---------------------------------------------------------------------------
# Service providers
# ---------------------------------------------------------------------------
def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> AuthService:
    """Get authentication service."""
    return AuthService(user_repo)


def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
) -> UserService:
    return UserService(user_repo)


def get_film_service(
    film_repo: FilmRepository = Depends(get_film_repository),
) -> FilmService:
    return FilmService(film_repo)


def get_equipment_config_service(
    config_repo: EquipmentConfigRepository = Depends(get_equipment_config_repository),
) -> EquipmentConfigService:
    return EquipmentConfigService(config_repo)


def get_experiment_service(
    experiment_repo: ExperimentRepository = Depends(get_experiment_repository),
    user_repo: UserRepository = Depends(get_user_repository),
    film_repo: FilmRepository = Depends(get_film_repository),
    config_repo: EquipmentConfigRepository = Depends(get_equipment_config_repository),
) -> ExperimentService:
    return ExperimentService(experiment_repo, user_repo, film_repo, config_repo)


def get_experiment_image_service(
    image_repo: ExperimentImageRepository = Depends(get_experiment_image_repository),
    experiment_repo: ExperimentRepository = Depends(get_experiment_repository),
) -> ExperimentImageService:
    return ExperimentImageService(image_repo, experiment_repo)


def get_image_analysis_service(
    image_repo: ExperimentImageRepository = Depends(get_experiment_image_repository),
    experiment_repo: ExperimentRepository = Depends(get_experiment_repository),
) -> ImageAnalysisService:
    return ImageAnalysisService(image_repo, experiment_repo)


def get_situation_service(
    situation_repo: SituationRepository = Depends(get_situation_repository),
) -> SituationService:
    return SituationService(situation_repo)


def get_cause_service(
    cause_repo: CauseRepository = Depends(get_cause_repository),
    situation_repo: SituationRepository = Depends(get_situation_repository),
) -> CauseService:
    return CauseService(cause_repo, situation_repo)


def get_advice_service(
    advice_repo: AdviceRepository = Depends(get_advice_repository),
    cause_repo: CauseRepository = Depends(get_cause_repository),
) -> AdviceService:
    return AdviceService(advice_repo, cause_repo)


# ---------------------------------------------------------------------------
# Auth dependencies (raise domain exceptions, NOT HTTPException)
# ---------------------------------------------------------------------------
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_users_db),
    user_service: UserService = Depends(get_user_service),
) -> UserRead:
    """Dependency to get the current authenticated user.

    Uses ``get_for_auth`` which bypasses the Redis cache and
    eagerly loads roles.  This ensures role-based checks
    (``get_current_admin``) always see up-to-date roles.
    """
    try:
        payload = verify_token(token)
    except TokenValidationError as exc:
        raise AuthenticationError(exc.message) from exc

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise AuthenticationError("Could not validate credentials")

    try:
        user_id = UUID(user_id_str)
    except ValueError as exc:
        raise AuthenticationError("Invalid user ID in token") from exc

    user = await user_service.get_for_auth(user_id, db)
    if not user.is_active:
        raise AuthenticationError("User account is inactive")
    return user


async def get_current_admin(
    current_user: UserRead = Depends(get_current_user),
) -> UserRead:
    """Dependency to ensure the current user is an admin."""
    if not any(role.name == "admin" for role in current_user.roles):
        raise AuthorizationError("Access forbidden: Admin privileges required")
    return current_user


# ---------------------------------------------------------------------------
# Type aliases for clean endpoint signatures
# ---------------------------------------------------------------------------

# Sessions
MainDBSession = Annotated[AsyncSession, Depends(get_main_db)]
UsersDBSession = Annotated[AsyncSession, Depends(get_users_db)]
KnowledgeDBSession = Annotated[AsyncSession, Depends(get_knowledge_db)]
RedisClient = Annotated[object, Depends(get_redis_client)]

# Repositories
UserRepo = Annotated[UserRepository, Depends(get_user_repository)]
ExperimentRepo = Annotated[ExperimentRepository, Depends(get_experiment_repository)]
FilmRepo = Annotated[FilmRepository, Depends(get_film_repository)]
EquipmentConfigRepo = Annotated[
    EquipmentConfigRepository, Depends(get_equipment_config_repository)
]
ExperimentImageRepo = Annotated[
    ExperimentImageRepository, Depends(get_experiment_image_repository)
]
SituationRepo = Annotated[SituationRepository, Depends(get_situation_repository)]
CauseRepo = Annotated[CauseRepository, Depends(get_cause_repository)]
AdviceRepo = Annotated[AdviceRepository, Depends(get_advice_repository)]

# Services
AuthSvc = Annotated[AuthService, Depends(get_auth_service)]
UserSvc = Annotated[UserService, Depends(get_user_service)]
FilmSvc = Annotated[FilmService, Depends(get_film_service)]
EquipmentConfigSvc = Annotated[
    EquipmentConfigService, Depends(get_equipment_config_service)
]
ExperimentSvc = Annotated[ExperimentService, Depends(get_experiment_service)]
ExperimentImageSvc = Annotated[
    ExperimentImageService, Depends(get_experiment_image_service)
]
ImageAnalysisSvc = Annotated[ImageAnalysisService, Depends(get_image_analysis_service)]
SituationSvc = Annotated[SituationService, Depends(get_situation_service)]
CauseSvc = Annotated[CauseService, Depends(get_cause_service)]
AdviceSvc = Annotated[AdviceService, Depends(get_advice_service)]

# Auth
CurrentUser = Annotated[UserRead, Depends(get_current_user)]
CurrentAdmin = Annotated[UserRead, Depends(get_current_admin)]
