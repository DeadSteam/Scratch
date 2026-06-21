"""Experiment service with business logic."""

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.tracing import get_tracer
from ..models.experiment import Experiment
from ..repositories.advice_repository import AdviceRepository
from ..repositories.cause_repository import CauseRepository
from ..repositories.equipment_config_repository import EquipmentConfigRepository
from ..repositories.experiment_repository import ExperimentRepository
from ..repositories.film_repository import FilmRepository
from ..repositories.situation_repository import SituationRepository
from ..repositories.user_repository import UserRepository
from ..schemas.experiment import (
    ExperimentCreate,
    ExperimentRead,
    ExperimentUpdate,
    KnowledgeCauseRead,
    KnowledgeSummary,
    ScratchResult,
)
from ..schemas.situation import SituationRead
from .base import BaseService
from .exceptions import NotFoundError

_tracer = get_tracer()


class ExperimentService(
    BaseService[Experiment, ExperimentCreate, ExperimentUpdate, ExperimentRead]
):
    """Experiment service with business validation."""

    def __init__(
        self,
        repository: ExperimentRepository,
        user_repository: UserRepository,
        film_repository: FilmRepository,
        config_repository: EquipmentConfigRepository,
        situation_repository: SituationRepository,
        cause_repository: CauseRepository,
        advice_repository: AdviceRepository,
    ):
        super().__init__(
            repository=repository,
            entity_name="Experiment",
            create_schema=ExperimentCreate,
            update_schema=ExperimentUpdate,
            read_schema=ExperimentRead,
        )
        self.experiment_repo = repository
        self.user_repo = user_repository
        self.film_repo = film_repository
        self.config_repo = config_repository
        self.situation_repo = situation_repository
        self.cause_repo = cause_repository
        self.advice_repo = advice_repository

    @staticmethod
    def _pick_reference_result(
        scratch_results: list[dict[str, Any]] | None,
    ) -> ScratchResult | None:
        if not scratch_results:
            return None
        candidates = [
            entry
            for entry in scratch_results
            if isinstance(entry, dict) and (entry.get("passes") or 0) == 0
        ]
        if not candidates:
            return None
        return ScratchResult.model_validate(candidates[0])

    @staticmethod
    def _pick_latest_result(
        scratch_results: list[dict[str, Any]] | None,
    ) -> ScratchResult | None:
        if not scratch_results:
            return None
        candidates = [
            entry
            for entry in scratch_results
            if isinstance(entry, dict) and (entry.get("passes") or 0) > 0
        ]
        if not candidates:
            return None
        latest = max(candidates, key=lambda entry: int(entry.get("passes") or 0))
        return ScratchResult.model_validate(latest)

    async def _build_knowledge_summary(
        self,
        experiment: Experiment,
        knowledge_session: AsyncSession | None,
        *,
        include_causes: bool = True,
    ) -> KnowledgeSummary | None:
        with _tracer.start_as_current_span(
            "experiment.build_knowledge_summary"
        ) as span:
            span.set_attribute("experiment.id", str(experiment.id))
            span.set_attribute("include_causes", include_causes)
            return await self._build_knowledge_summary_inner(
                experiment, knowledge_session, include_causes=include_causes
            )

    async def _build_knowledge_summary_inner(
        self,
        experiment: Experiment,
        knowledge_session: AsyncSession | None,
        *,
        include_causes: bool = True,
    ) -> KnowledgeSummary | None:
        scratch_results = experiment.scratch_results or []
        reference_result = self._pick_reference_result(scratch_results)
        latest_result = self._pick_latest_result(scratch_results)

        if reference_result is None and latest_result is None:
            return None

        delta = None
        if reference_result is not None and latest_result is not None:
            delta = round(
                latest_result.scratch_index - reference_result.scratch_index, 3
            )

        summary = KnowledgeSummary(
            controlled_param=None,
            delta=delta,
            reference_result=reference_result,
            latest_result=latest_result,
            situation=None,
            causes=[],
        )

        if knowledge_session is None or delta is None:
            return summary

        situation = await self.situation_repo.find_by_value_in_ranges(
            delta,
            knowledge_session,
        )
        if situation is None:
            return summary

        if not include_causes:
            return summary.model_copy(
                update={
                    "situation": SituationRead.model_validate(situation),
                    "causes": [],
                }
            )

        causes = await self.cause_repo.get_by_situation_id(
            situation.id,
            knowledge_session,
            skip=0,
            limit=100,
        )

        # B10: batch-load advices for ALL causes in one query instead of
        # one query per cause (N+1).
        advices_by_cause = await self.advice_repo.get_by_cause_ids(
            [c.id for c in causes],
            knowledge_session,
        )

        knowledge_causes: list[KnowledgeCauseRead] = [
            KnowledgeCauseRead.model_validate(
                {
                    "id": cause.id,
                    "situation_id": cause.situation_id,
                    "description": cause.description,
                    "advices": advices_by_cause.get(cause.id, []),
                }
            )
            for cause in causes
        ]

        return summary.model_copy(
            update={
                "situation": SituationRead.model_validate(situation),
                "causes": knowledge_causes,
            }
        )

    async def _build_experiment_read(
        self,
        experiment: Experiment,
        knowledge_session: AsyncSession | None = None,
        *,
        include_knowledge_causes: bool = True,
    ) -> ExperimentRead:
        experiment_read = self.read_schema.model_validate(experiment)
        knowledge_summary = await self._build_knowledge_summary(
            experiment,
            knowledge_session,
            include_causes=include_knowledge_causes,
        )
        return experiment_read.model_copy(
            update={"knowledge_summary": knowledge_summary}
        )

    async def get_by_id(
        self,
        entity_id: UUID,
        session: AsyncSession,
        knowledge_session: AsyncSession | None = None,
    ) -> ExperimentRead:
        """Get experiment by ID with relationships loaded."""
        experiment = await self.experiment_repo.get_by_id_with_relations(
            entity_id, session
        )
        if not experiment:
            raise NotFoundError(self.entity_name, entity_id)
        return await self._build_experiment_read(experiment, knowledge_session)

    async def get_all(
        self, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[ExperimentRead]:
        """Get all experiments with relationships loaded."""
        experiments = await self.experiment_repo.get_all_with_relations(
            session, skip, limit
        )
        return [self.read_schema.model_validate(e) for e in experiments]

    async def create_for_user(
        self,
        data: ExperimentCreate,
        user_id: UUID,
        session: AsyncSession,
    ) -> ExperimentRead:
        """Create experiment owned by `user_id`. Validates FKs.

        Server-controlled fields (user_id, scratch_results) are NOT taken
        from the payload — they're set here. See S1 in the audit.
        """
        if not await self.film_repo.exists(data.film_id, session):
            raise NotFoundError("Film", data.film_id)
        if not await self.config_repo.exists(data.config_id, session):
            raise NotFoundError("EquipmentConfig", data.config_id)

        payload = data.model_dump(exclude_unset=True)
        payload["user_id"] = user_id
        # Never accept client-supplied analysis results
        payload.pop("scratch_results", None)

        entity = await self.experiment_repo.create(payload, session)
        return self.read_schema.model_validate(entity)

    async def create(
        self, data: ExperimentCreate, session: AsyncSession
    ) -> ExperimentRead:
        """Legacy entry point. Use create_for_user so user_id is server-set."""
        raise RuntimeError(
            "ExperimentService.create() is disabled — "
            "use create_for_user(data, user_id, session)."
        )

    async def update(
        self, entity_id: UUID, data: ExperimentUpdate, session: AsyncSession
    ) -> ExperimentRead:
        """Update experiment with validation of foreign keys."""
        if data.film_id and not await self.film_repo.exists(data.film_id, session):
            raise NotFoundError("Film", data.film_id)
        if data.config_id and not await self.config_repo.exists(
            data.config_id, session
        ):
            raise NotFoundError("EquipmentConfig", data.config_id)
        if not await self.experiment_repo.exists(entity_id, session):
            raise NotFoundError(self.entity_name, entity_id)

        entity_data = data.model_dump(exclude_unset=True)
        if not entity_data:
            experiment = await self.experiment_repo.get_by_id_with_relations(
                entity_id, session
            )
            if not experiment:
                raise NotFoundError(self.entity_name, entity_id)
            return self.read_schema.model_validate(experiment)

        await self.experiment_repo.update(entity_id, entity_data, session)
        experiment = await self.experiment_repo.get_by_id_with_relations(
            entity_id, session
        )
        if not experiment:
            raise NotFoundError(self.entity_name, entity_id)
        return self.read_schema.model_validate(experiment)

    async def get_by_user_id(
        self,
        user_id: UUID,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        knowledge_session: AsyncSession | None = None,
    ) -> list[ExperimentRead]:
        """Get experiments by user ID."""
        try:
            experiments = await self.experiment_repo.get_by_user_id_cached(
                user_id, session, skip, limit
            )
            result: list[ExperimentRead] = []
            for exp in experiments:
                try:
                    exp_read = await self._build_experiment_read(
                        exp,
                        knowledge_session,
                        include_knowledge_causes=False,
                    )
                    result.append(exp_read)
                except Exception:
                    self._logger.warning(
                        "experiment_validation_failed",
                        experiment_id=str(exp.id),
                    )
                    result.append(
                        self.read_schema.model_validate(
                            {
                                "id": exp.id,
                                "film_id": exp.film_id,
                                "config_id": exp.config_id,
                                "user_id": exp.user_id,
                                "date": exp.date,
                                "rect_coords": exp.rect_coords,
                                "weight": exp.weight,
                                "has_fabric": exp.has_fabric,
                                "scratch_results": exp.scratch_results,
                            },
                            from_attributes=True,
                        )
                    )
            return result
        except Exception:
            self._logger.exception(
                "get_by_user_id_failed",
                user_id=str(user_id),
            )
            raise

    # ---------------------------------------------------------------
    # B3: single unified entry point. All `get_by_X` / `count_by_X`
    # methods route through here.
    # ---------------------------------------------------------------
    async def list_experiments(
        self,
        session: AsyncSession,
        *,
        user_id: UUID | None = None,
        film_id: UUID | None = None,
        config_id: UUID | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ExperimentRead]:
        """List experiments by any combination of user/film/config filters."""
        if film_id is not None and not await self.film_repo.exists(film_id, session):
            raise NotFoundError("Film", film_id)
        if config_id is not None and not await self.config_repo.exists(
            config_id, session
        ):
            raise NotFoundError("EquipmentConfig", config_id)
        experiments = await self.experiment_repo.list_experiments(
            session,
            user_id=user_id,
            film_id=film_id,
            config_id=config_id,
            skip=skip,
            limit=limit,
        )
        return [self.read_schema.model_validate(e) for e in experiments]

    async def count_experiments(
        self,
        session: AsyncSession,
        *,
        user_id: UUID | None = None,
        film_id: UUID | None = None,
        config_id: UUID | None = None,
    ) -> int:
        return await self.experiment_repo.count_experiments(
            session, user_id=user_id, film_id=film_id, config_id=config_id
        )

    # --- Back-compat facades -----------------------------------------
    async def get_by_film_id(
        self,
        film_id: UUID,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ExperimentRead]:
        return await self.list_experiments(
            session, film_id=film_id, skip=skip, limit=limit
        )

    async def get_by_config_id(
        self,
        config_id: UUID,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ExperimentRead]:
        return await self.list_experiments(
            session, config_id=config_id, skip=skip, limit=limit
        )

    async def get_with_images(
        self,
        experiment_id: UUID,
        session: AsyncSession,
        knowledge_session: AsyncSession | None = None,
    ) -> ExperimentRead:
        """Get experiment with all related images."""
        experiment = await self.experiment_repo.get_with_images(experiment_id, session)
        if not experiment:
            raise NotFoundError("Experiment", experiment_id)
        return await self._build_experiment_read(experiment, knowledge_session)

    async def count_by_user_id(self, user_id: UUID, session: AsyncSession) -> int:
        return await self.count_experiments(session, user_id=user_id)

    async def count_by_film_id(self, film_id: UUID, session: AsyncSession) -> int:
        return await self.count_experiments(session, film_id=film_id)

    async def count_by_config_id(self, config_id: UUID, session: AsyncSession) -> int:
        return await self.count_experiments(session, config_id=config_id)

    async def get_by_film_id_for_user(
        self,
        film_id: UUID,
        user_id: UUID,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ExperimentRead]:
        return await self.list_experiments(
            session, film_id=film_id, user_id=user_id, skip=skip, limit=limit
        )

    async def get_by_config_id_for_user(
        self,
        config_id: UUID,
        user_id: UUID,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ExperimentRead]:
        return await self.list_experiments(
            session, config_id=config_id, user_id=user_id, skip=skip, limit=limit
        )

    async def count_by_film_id_for_user(
        self, film_id: UUID, user_id: UUID, session: AsyncSession
    ) -> int:
        return await self.count_experiments(session, film_id=film_id, user_id=user_id)

    async def count_by_config_id_for_user(
        self, config_id: UUID, user_id: UUID, session: AsyncSession
    ) -> int:
        return await self.count_experiments(
            session, config_id=config_id, user_id=user_id
        )
