"""Demo / reference data: seed empty catalog and knowledge tables on startup."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.equipment_config import EquipmentConfig
from ..models.film import Film
from ..models.knowledge import Advice, Cause, Situation
from .config import settings
from .logging_config import get_logger

logger = get_logger(__name__)


async def _count_rows(session: AsyncSession, model: type) -> int:
    result = await session.scalar(select(func.count()).select_from(model))
    return int(result or 0)


async def seed_main_catalog_if_empty(session: AsyncSession) -> None:
    """Insert default films and equipment configs when tables have no rows."""
    films_n = await _count_rows(session, Film)
    if films_n == 0:
        session.add_all(
            [
                Film(
                    name="H&NO-Muster",
                    coating_name="H&NB+M",
                    coating_thickness=4.0,
                ),
            ]
        )
        logger.info("seed_films_inserted", count=1)

    configs_n = await _count_rows(session, EquipmentConfig)
    if configs_n == 0:
        session.add_all(
            [
                EquipmentConfig(
                    name="Шариковая",
                    head_type="Титан",
                    description="Головка из сплава титана",
                ),
            ]
        )
        logger.info("seed_equipment_configs_inserted", count=1)


async def seed_knowledge_if_empty(session: AsyncSession) -> None:
    """Insert local knowledge data when knowledge DB is empty."""
    situations_n = await _count_rows(session, Situation)
    if situations_n > 0:
        return

    s1 = Situation(
        controlled_param="модуль изменения индекс зарапанности",
        min_value=0.0,
        max_value=0.015,
        label="Хорошо",
        severity="success",
        description="Хорошая износостойкость",
    )
    s2 = Situation(
        controlled_param="модуль изменения индекс зарапанности",
        min_value=0.01500001,
        max_value=0.02,
        label="Средне",
        severity="warning",
        description="Средняя износостойкость",
    )
    s3 = Situation(
        controlled_param="модуль изменения индекс зарапанности",
        min_value=0.0201,
        max_value=1.0,
        label="Критично",
        severity="error",
        description="Плохая изностойкость",
    )
    session.add_all([s1, s2, s3])
    await session.flush()

    c1 = Cause(
        situation_id=s1.id,
        description="Оптимальное соотношение компонентов",
    )
    c2 = Cause(
        situation_id=s2.id,
        description="Недостаточная степень отверждения",
    )
    c3 = Cause(
        situation_id=s3.id,
        description="Низкая адгезия покрытия",
    )
    session.add_all([c1, c2, c3])
    await session.flush()

    session.add_all(
        [
            Advice(
                cause_id=c1.id,
                description="Повторить тест на новой партии",
            ),
            Advice(
                cause_id=c1.id,
                description="Сохранить текущую рецептуру",
            ),
            Advice(
                cause_id=c2.id,
                description="Стабилизировать толщину покрытия",
            ),
            Advice(
                cause_id=c2.id,
                description="Проверить однородность смеси",
            ),
            Advice(
                cause_id=c3.id,
                description="Пересмотреть состав рецептуры",
            ),
        ]
    )
    logger.info("seed_knowledge_inserted", situations=3, causes=3, advices=5)


async def seed_reference_data_on_startup() -> None:
    """Run catalog + knowledge seeding when enabled and DBs are available."""
    if not settings.AUTO_SEED_REFERENCE_DATA:
        logger.info("auto_seed_reference_data_disabled")
        return

    from .database import (
        KnowledgeSessionLocal,
        get_db_transaction,
        get_knowledge_db_transaction,
    )

    try:
        async with get_db_transaction() as session:
            await seed_main_catalog_if_empty(session)
    except Exception:
        logger.exception("seed_main_catalog_failed")

    if KnowledgeSessionLocal is None:
        logger.info("knowledge_seed_skipped", reason="KNOWLEDGE_DATABASE_URL not set")
        return

    try:
        async with get_knowledge_db_transaction() as session:
            await seed_knowledge_if_empty(session)
    except Exception:
        logger.exception("seed_knowledge_failed")
