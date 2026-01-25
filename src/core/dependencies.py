from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
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
from ..services import (
    EquipmentConfigService,
    ExperimentImageService,
    ExperimentService,
    FilmService,
    UserService,
)
from ..services.advice_service import AdviceService
from ..services.cause_service import CauseService
from ..services.image_analysis_service import ImageAnalysisService
from ..services.situation_service import SituationService
from .database import get_db_session, get_knowledge_db_session, get_users_db_session
from .redis import get_redis_client


# Database dependencies
async def get_main_db() -> AsyncGenerator[AsyncSession, None]:
    """Get main database session."""
    async for session in get_db_session():
        yield session


async def get_users_db() -> AsyncGenerator[AsyncSession, None]:
    """Get users database session."""
    async for session in get_users_db_session():
        yield session


async def get_knowledge_db() -> AsyncGenerator[AsyncSession, None]:
    """Get knowledge base database session."""
    async for session in get_knowledge_db_session():
        yield session


# Repository dependencies
def get_user_repository() -> UserRepository:
    """Get user repository instance."""
    return UserRepository()


def get_experiment_repository() -> ExperimentRepository:
    """Get experiment repository instance."""
    return ExperimentRepository()


def get_film_repository() -> FilmRepository:
    """Get film repository instance."""
    return FilmRepository()


def get_equipment_config_repository() -> EquipmentConfigRepository:
    """Get equipment config repository instance."""
    return EquipmentConfigRepository()


def get_experiment_image_repository() -> ExperimentImageRepository:
    """Get experiment image repository instance."""
    return ExperimentImageRepository()


def get_situation_repository() -> SituationRepository:
    return SituationRepository()


def get_cause_repository() -> CauseRepository:
    return CauseRepository()


def get_advice_repository() -> AdviceRepository:
    return AdviceRepository()


# Service dependencies
def get_user_service(user_repo: UserRepository = Depends(get_user_repository)) -> UserService:
    """Get user service instance."""
    return UserService(user_repo)


def get_film_service(film_repo: FilmRepository = Depends(get_film_repository)) -> FilmService:
    """Get film service instance."""
    return FilmService(film_repo)


def get_equipment_config_service(
    config_repo: EquipmentConfigRepository = Depends(get_equipment_config_repository),
) -> EquipmentConfigService:
    """Get equipment config service instance."""
    return EquipmentConfigService(config_repo)


def get_experiment_service(
    experiment_repo: ExperimentRepository = Depends(get_experiment_repository),
    user_repo: UserRepository = Depends(get_user_repository),
    film_repo: FilmRepository = Depends(get_film_repository),
    config_repo: EquipmentConfigRepository = Depends(get_equipment_config_repository),
) -> ExperimentService:
    """Get experiment service instance."""
    return ExperimentService(experiment_repo, user_repo, film_repo, config_repo)


def get_experiment_image_service(
    image_repo: ExperimentImageRepository = Depends(get_experiment_image_repository),
    experiment_repo: ExperimentRepository = Depends(get_experiment_repository),
) -> ExperimentImageService:
    """Get experiment image service instance."""
    return ExperimentImageService(image_repo, experiment_repo)


def get_image_analysis_service(
    image_repo: ExperimentImageRepository = Depends(get_experiment_image_repository),
    experiment_repo: ExperimentRepository = Depends(get_experiment_repository),
) -> ImageAnalysisService:
    """Get image analysis service instance."""
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


# Type aliases for dependency injection
MainDBSession = Annotated[AsyncSession, Depends(get_main_db)]
UsersDBSession = Annotated[AsyncSession, Depends(get_users_db)]
KnowledgeDBSession = Annotated[AsyncSession, Depends(get_knowledge_db)]
RedisClient = Annotated[object, Depends(get_redis_client)]

# Repository DI
UserRepo = Annotated[UserRepository, Depends(get_user_repository)]
ExperimentRepo = Annotated[ExperimentRepository, Depends(get_experiment_repository)]
FilmRepo = Annotated[FilmRepository, Depends(get_film_repository)]
EquipmentConfigRepo = Annotated[EquipmentConfigRepository, Depends(get_equipment_config_repository)]
ExperimentImageRepo = Annotated[ExperimentImageRepository, Depends(get_experiment_image_repository)]
SituationRepo = Annotated[SituationRepository, Depends(get_situation_repository)]
CauseRepo = Annotated[CauseRepository, Depends(get_cause_repository)]
AdviceRepo = Annotated[AdviceRepository, Depends(get_advice_repository)]

# Service DI
UserSvc = Annotated[UserService, Depends(get_user_service)]
FilmSvc = Annotated[FilmService, Depends(get_film_service)]
EquipmentConfigSvc = Annotated[EquipmentConfigService, Depends(get_equipment_config_service)]
ExperimentSvc = Annotated[ExperimentService, Depends(get_experiment_service)]
ExperimentImageSvc = Annotated[ExperimentImageService, Depends(get_experiment_image_service)]
ImageAnalysisSvc = Annotated[ImageAnalysisService, Depends(get_image_analysis_service)]
SituationSvc = Annotated[SituationService, Depends(get_situation_service)]
CauseSvc = Annotated[CauseService, Depends(get_cause_service)]
AdviceSvc = Annotated[AdviceService, Depends(get_advice_service)]
