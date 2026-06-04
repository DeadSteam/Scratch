from typing import Any, cast
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import defer

from ..models.image import ExperimentImage
from .base import CachedRepositoryImpl


class ExperimentImageRepository(CachedRepositoryImpl[ExperimentImage]):
    """Experiment image repository implementation."""

    def __init__(self) -> None:
        super().__init__(ExperimentImage)

    async def get_by_experiment_id(
        self,
        experiment_id: UUID,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        *,
        include_data: bool = False,
    ) -> list[ExperimentImage]:
        """Get images by experiment ID.

        ``include_data``:
            False (default): defers the ``image_data`` BYTEA column. The
                list-images HTTP endpoint only returns id/passes/mime_type
                in JSON, but a plain SELECT * still drags every image's
                raw bytes out of Postgres TOAST + hydrates them — the
                difference between ~17 ms and ~114 ms on experiments with
                many uploads.
            True: required by ImageAnalysisService.recalculate_experiment,
                which actually walks ``image_data`` for every image. Without
                this flag we'd hit N+1 (one extra SELECT per row to lazily
                load the deferred column).
        """
        stmt = select(ExperimentImage)
        if not include_data:
            stmt = stmt.options(defer(ExperimentImage.image_data))
        stmt = (
            stmt.where(ExperimentImage.experiment_id == experiment_id)
            .order_by(ExperimentImage.passes.asc(), ExperimentImage.id.asc())
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def delete_by_experiment_id(
        self, experiment_id: UUID, session: AsyncSession
    ) -> int:
        """Delete all images for an experiment.

        No commit — managed by session dependency.
        """
        stmt = delete(ExperimentImage).where(
            ExperimentImage.experiment_id == experiment_id
        )
        result = await session.execute(stmt)
        return cast(CursorResult[Any], result).rowcount

    async def count_by_experiment_id(
        self, experiment_id: UUID, session: AsyncSession
    ) -> int:
        """Count images for an experiment."""

        result = await session.execute(
            select(func.count(ExperimentImage.id)).where(
                ExperimentImage.experiment_id == experiment_id
            )
        )
        return result.scalar() or 0
