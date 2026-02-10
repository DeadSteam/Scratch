"""Image analysis service for scratch resistance calculation.

Supports two modes of operation:

1. **Incremental** (preferred): ``analyze_and_save_single()`` calculates the
   scratch index for ONE image and appends the result to the experiment's
   ``scratch_results`` JSON array.  No existing entries are recalculated.

2. **Full recalculation**: ``recalculate_experiment()`` recomputes scratch
   indices for every image in the experiment.  Use when the ROI
   (``rect_coords``) changes or when a full audit is needed.
"""

from io import BytesIO
from typing import Any, cast
from uuid import UUID

import numpy as np
from numpy.typing import NDArray
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.logging_config import get_logger
from ..repositories.experiment_repository import ExperimentRepository
from ..repositories.image_repository import ExperimentImageRepository
from .exceptions import NotFoundError
from .exceptions import ValidationError as ServiceValidationError

logger = get_logger(__name__)


class ImageAnalysisService:
    """Service for analyzing experiment images."""

    def __init__(
        self,
        image_repository: ExperimentImageRepository,
        experiment_repository: ExperimentRepository,
    ):
        self.image_repo = image_repository
        self.experiment_repo = experiment_repository

    # ------------------------------------------------------------------
    # Pure computation (no I/O)
    # ------------------------------------------------------------------

    def convert_to_grayscale(
        self, image_array: NDArray[Any]
    ) -> NDArray[np.uint8]:
        """Convert RGB image to Grayscale.

        Formula: Grayscale(i,j) = 0.3*R + 0.59*G + 0.11*B
        """
        if len(image_array.shape) != 3 or image_array.shape[2] != 3:
            raise ServiceValidationError(
                "Image must be RGB format (H, W, 3)"
            )
        r = image_array[:, :, 0].astype(np.float32)
        g = image_array[:, :, 1].astype(np.float32)
        b = image_array[:, :, 2].astype(np.float32)
        grayscale = 0.3 * r + 0.59 * g + 0.11 * b
        return cast(NDArray[np.uint8], grayscale.astype(np.uint8))

    def calculate_histogram(
        self, grayscale_image: NDArray[Any]
    ) -> dict[int, int]:
        """Brightness histogram (level 0-255 → pixel count)."""
        histogram, _ = np.histogram(
            grayscale_image.flatten(), bins=256, range=(0, 256)
        )
        return {
            q: int(count)
            for q, count in enumerate(histogram)
            if count > 0
        }

    def calculate_scratch_index(
        self,
        histogram: dict[int, int],
        total_pixels: int,
        weights: dict[int, float] | None = None,
    ) -> float:
        """Scratch index via linear convolution.

        U(X) = sum( w_q * (count_q / total_pixels) )
        """
        if total_pixels == 0:
            return 0.0
        if weights is None:
            weights = {q: q / 255.0 for q in range(256)}
        scratch_index = 0.0
        for q, count in histogram.items():
            w = weights.get(q, q / 255.0)
            scratch_index += w * (count / total_pixels)
        return scratch_index

    def analyze_image(
        self,
        image_data: bytes,
        rect_coords: list[float] | None = None,
    ) -> dict[str, Any]:
        """Analyze a single image: grayscale + histogram + stats."""
        try:
            from PIL import Image
        except ImportError:
            raise ServiceValidationError(
                "PIL (Pillow) is required for image processing"
            ) from None

        image = Image.open(BytesIO(image_data))
        if image.mode != "RGB":
            image = image.convert("RGB")

        # ROI crop
        if rect_coords and len(rect_coords) == 4:
            x, y, w, h = (int(v) for v in rect_coords)
            img_w, img_h = image.size
            if x < 0 or y < 0 or x + w > img_w or y + h > img_h:
                raise ServiceValidationError(
                    f"ROI out of bounds: image {img_w}x{img_h}, "
                    f"ROI ({x}, {y}, {w}, {h})"
                )
            image = image.crop((x, y, x + w, y + h))

        image_array = np.array(image)
        grayscale = self.convert_to_grayscale(image_array)
        histogram = self.calculate_histogram(grayscale)

        total_pixels = int(grayscale.size) or 1

        return {
            "grayscale_shape": grayscale.shape,
            "histogram": histogram,
            "total_pixels": total_pixels,
            "brightness_levels_count": len(histogram),
        }

    # ------------------------------------------------------------------
    # Incremental: analyze ONE image and append to scratch_results
    # ------------------------------------------------------------------

    async def analyze_and_save_single(
        self,
        image_id: UUID,
        session: AsyncSession,
    ) -> dict[str, Any]:
        """Analyze a single image and append its scratch index
        to the experiment's ``scratch_results`` array.

        If an entry for this ``image_id`` already exists in the array
        it is **replaced** (idempotent).

        Returns the computed entry dict.
        """
        image = await self.image_repo.get_by_id(image_id, session)
        if not image:
            raise NotFoundError("ExperimentImage", image_id)

        experiment = await self.experiment_repo.get_by_id(
            image.experiment_id, session
        )
        if not experiment:
            raise NotFoundError("Experiment", image.experiment_id)

        rect_coords = experiment.rect_coords

        # Analyze (fallback to full image if ROI is out of bounds)
        try:
            analysis = self.analyze_image(image.image_data, rect_coords)
        except ServiceValidationError:
            analysis = self.analyze_image(image.image_data, None)

        scratch_index = self.calculate_scratch_index(
            analysis["histogram"], analysis["total_pixels"]
        )

        # Build the entry
        entry: dict[str, Any] = {
            "image_id": str(image_id),
            "passes": image.passes,
            "scratch_index": scratch_index,
            "total_pixels": analysis["total_pixels"],
        }

        # Append / replace in scratch_results
        existing: list[dict[str, Any]] = list(
            experiment.scratch_results or []
        )
        # Remove previous entry for same image (idempotent)
        existing = [
            e for e in existing if e.get("image_id") != str(image_id)
        ]
        existing.append(entry)

        await self.experiment_repo.update(
            experiment.id,
            {"scratch_results": existing},
            session,
        )

        logger.info(
            "single_image_analyzed",
            image_id=str(image_id),
            experiment_id=str(experiment.id),
            scratch_index=scratch_index,
        )

        return entry

    # ------------------------------------------------------------------
    # Full recalculation (when ROI changes or on explicit request)
    # ------------------------------------------------------------------

    async def recalculate_experiment(
        self,
        experiment_id: UUID,
        session: AsyncSession,
    ) -> dict[str, Any]:
        """Recalculate scratch indices for ALL images in experiment.

        Overwrites the entire ``scratch_results`` array.
        Use when ``rect_coords`` changes or for a full audit.
        """
        experiment = await self.experiment_repo.get_by_id(
            experiment_id, session
        )
        if not experiment:
            raise NotFoundError("Experiment", experiment_id)

        rect_coords = experiment.rect_coords
        images = await self.image_repo.get_by_experiment_id(
            experiment_id, session, skip=0, limit=10000
        )

        results: list[dict[str, Any]] = []
        for image in images:
            try:
                analysis = self.analyze_image(
                    image.image_data, rect_coords
                )
            except ServiceValidationError:
                analysis = self.analyze_image(image.image_data, None)

            si = self.calculate_scratch_index(
                analysis["histogram"], analysis["total_pixels"]
            )
            results.append(
                {
                    "image_id": str(image.id),
                    "passes": image.passes,
                    "scratch_index": si,
                    "total_pixels": analysis["total_pixels"],
                }
            )

        # Sort by passes for consistent ordering
        results.sort(key=lambda r: r.get("passes", 0))

        await self.experiment_repo.update(
            experiment_id,
            {"scratch_results": results},
            session,
        )

        # Summary stats
        indices = [r["scratch_index"] for r in results]
        summary = {
            "count": len(results),
            "average": float(np.mean(indices)) if indices else 0.0,
            "max": float(np.max(indices)) if indices else 0.0,
            "min": float(np.min(indices)) if indices else 0.0,
        }

        logger.info(
            "experiment_recalculated",
            experiment_id=str(experiment_id),
            image_count=len(results),
        )

        return {
            "experiment_id": str(experiment_id),
            "scratch_results": results,
            "summary": summary,
        }

    # ------------------------------------------------------------------
    # Read-only helpers (no writes)
    # ------------------------------------------------------------------

    async def get_image_histogram(
        self, image_id: UUID, session: AsyncSession
    ) -> dict[str, Any]:
        """Get brightness histogram for a single image."""
        image = await self.image_repo.get_by_id(image_id, session)
        if not image:
            raise NotFoundError("ExperimentImage", image_id)
        experiment = await self.experiment_repo.get_by_id(
            image.experiment_id, session
        )
        rect_coords = experiment.rect_coords if experiment else None
        try:
            analysis = self.analyze_image(image.image_data, rect_coords)
        except ServiceValidationError:
            analysis = self.analyze_image(image.image_data, None)
        return {
            "image_id": str(image_id),
            "histogram": analysis["histogram"],
            "statistics": {
                "total_pixels": analysis["total_pixels"],
                "brightness_levels_count": analysis[
                    "brightness_levels_count"
                ],
            },
        }

    async def quick_analysis(
        self,
        experiment_id: UUID,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Quick per-image stats (no write, no recalculation)."""
        experiment = await self.experiment_repo.get_by_id(
            experiment_id, session
        )
        rect_coords = experiment.rect_coords if experiment else None
        images = await self.image_repo.get_by_experiment_id(
            experiment_id, session, skip, limit
        )
        if not images:
            return {
                "experiment_id": str(experiment_id),
                "images": [],
                "count": 0,
            }
        results = []
        for image in images:
            try:
                a = self.analyze_image(image.image_data, rect_coords)
            except ServiceValidationError:
                a = self.analyze_image(image.image_data, None)
            results.append(
                {
                    "image_id": str(image.id),
                    "passes": image.passes,
                    "total_pixels": a["total_pixels"],
                }
            )
        return {
            "experiment_id": str(experiment_id),
            "images": results,
            "count": len(results),
        }
