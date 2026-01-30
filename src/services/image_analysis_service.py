"""Image analysis service for scratch resistance calculation."""

from io import BytesIO
from typing import Any, cast
from uuid import UUID

import numpy as np
from numpy.typing import NDArray
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories.experiment_repository import ExperimentRepository
from ..repositories.image_repository import ExperimentImageRepository
from .exceptions import NotFoundError
from .exceptions import ValidationError as ServiceValidationError


class ImageAnalysisService:
    """Service for analyzing experiment images and calculating scratch index."""

    def __init__(
        self,
        image_repository: ExperimentImageRepository,
        experiment_repository: ExperimentRepository,
    ):
        self.image_repo = image_repository
        self.experiment_repo = experiment_repository

    def convert_to_grayscale(self, image_array: NDArray[Any]) -> NDArray[np.uint8]:
        """
        Convert RGB image to Grayscale using the formula:
        Grayscale(i,j) = 0.3 * R(i,j) + 0.59 * G(i,j) + 0.11 * B(i,j)

        Args:
            image_array: RGB image as numpy array (H, W, 3)

        Returns:
            Grayscale image as numpy array (H, W)
        """
        if len(image_array.shape) != 3 or image_array.shape[2] != 3:
            raise ServiceValidationError("Image must be RGB format (H, W, 3)")

        # Extract RGB channels
        r = image_array[:, :, 0].astype(np.float32)
        g = image_array[:, :, 1].astype(np.float32)
        b = image_array[:, :, 2].astype(np.float32)

        # Apply grayscale formula
        grayscale = 0.3 * r + 0.59 * g + 0.11 * b

        return cast(NDArray[np.uint8], grayscale.astype(np.uint8))

    def calculate_histogram(self, grayscale_image: NDArray[Any]) -> dict[int, int]:
        """
        Calculate histogram for grayscale image.

        Args:
            grayscale_image: Grayscale image (H, W)

        Returns:
            Dictionary mapping brightness level (0-255) to pixel count
        """
        # Flatten image and calculate histogram
        histogram, _ = np.histogram(grayscale_image.flatten(), bins=256, range=(0, 256))

        # Convert to dict for easier handling
        return {q: int(count) for q, count in enumerate(histogram) if count > 0}

    def calculate_scratch_index(
        self,
        histogram: dict[int, int],
        total_pixels: int,
        weights: dict[int, float] | None = None,
    ) -> float:
        """
        Calculate scratch index for a single image using linear convolution of criteria.
        Formula: U(X) = Σ(w_q * (count_q / total_pixels))

        Args:
            histogram: Brightness histogram for a single image
            total_pixels: Total number of pixels in the analyzed region (ROI)
            weights: Custom weights per brightness (0-255).
                    If None, use q/255 (whiter = higher weight).

        Returns:
            Scratch index value (normalized ratio, independent of ROI size)
        """
        if total_pixels == 0:
            return 0.0

        if weights is None:
            weights = {q: q / 255.0 for q in range(256)}

        scratch_index = 0.0
        for q, count in histogram.items():
            w = weights.get(q, q / 255.0)
            pixel_ratio = count / total_pixels
            scratch_index += w * pixel_ratio

        return scratch_index

    def analyze_image(
        self, image_data: bytes, rect_coords: list[float] | None = None
    ) -> dict[str, Any]:
        """
        Analyze a single image: convert to grayscale and calculate histogram.

        Args:
            image_data: Raw image bytes
            rect_coords: Optional ROI [x, y, width, height] to crop before analysis

        Returns:
            Analysis results with grayscale data, histogram, and statistics
        """
        try:
            # Try to import PIL for image loading
            from PIL import Image
        except ImportError:
            raise ServiceValidationError(
                "PIL (Pillow) is required for image processing"
            ) from None

        # Load image from bytes
        image = Image.open(BytesIO(image_data))

        # Convert to RGB if needed
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Apply ROI cropping if coordinates are provided
        if rect_coords and len(rect_coords) == 4:
            x, y, width, height = rect_coords
            # Convert to integers (PIL requires int coordinates)
            x = int(x)
            y = int(y)
            width = int(width)
            height = int(height)

            # Validate coordinates
            img_width, img_height = image.size
            if x < 0 or y < 0 or x + width > img_width or y + height > img_height:
                raise ServiceValidationError(
                    f"ROI coordinates out of bounds: "
                    f"image size ({img_width}x{img_height}), "
                    f"ROI ({x}, {y}, {width}, {height})"
                )

            # Crop image to ROI
            image = image.crop((x, y, x + width, y + height))

        # Convert to numpy array
        image_array = np.array(image)

        # Convert to grayscale
        grayscale = self.convert_to_grayscale(image_array)

        # Calculate histogram
        histogram = self.calculate_histogram(grayscale)

        total_pixels = int(grayscale.size)
        if total_pixels == 0:
            total_pixels = 1  # avoid division by zero

        if histogram:
            dominant_brightness, dominant_count = max(
                histogram.items(), key=lambda item: item[1]
            )
        else:
            dominant_brightness, dominant_count = 0, 0

        average_brightness_ratio = dominant_count / total_pixels
        weighted_average_brightness = sum(
            q * (count / total_pixels) for q, count in histogram.items()
        )

        return {
            "grayscale_shape": grayscale.shape,
            "histogram": histogram,
            "total_pixels": total_pixels,
            "brightness_levels_count": len(histogram),
            "dominant_brightness": dominant_brightness,
            "average_brightness_ratio": average_brightness_ratio,
            "weighted_average_brightness": weighted_average_brightness,
        }

    async def analyze_experiment_images(
        self,
        experiment_id: UUID,
        reference_image_id: UUID,
        scratched_image_ids: list[UUID],
        session: AsyncSession,
    ) -> dict[str, Any]:
        """
        Analyze experiment images and calculate scratch resistance metrics.

        Args:
            experiment_id: Experiment ID
            reference_image_id: ID of reference (non-scratched) image
            scratched_image_ids: List of scratched image IDs
            session: Database session

        Returns:
            Complete analysis results with scratch indices
        """
        # Validate experiment exists and get ROI coordinates
        experiment = await self.experiment_repo.get_by_id(experiment_id, session)
        if not experiment:
            raise NotFoundError("Experiment", experiment_id)

        # Get ROI coordinates from experiment (rect_coords: [x, y, width, height])
        rect_coords = (
            experiment.rect_coords if hasattr(experiment, "rect_coords") else None
        )

        # Get reference image
        reference_image = await self.image_repo.get_by_id(reference_image_id, session)
        if not reference_image:
            raise NotFoundError("ExperimentImage", reference_image_id)

        if reference_image.experiment_id != experiment_id:
            raise ServiceValidationError(
                "Reference image does not belong to this experiment"
            )

        # Analyze reference image with ROI cropping
        reference_analysis = self.analyze_image(reference_image.image_data, rect_coords)

        # Analyze scratched images
        scratched_analyses = []
        scratch_indices = []

        for scratched_id in scratched_image_ids:
            # Get scratched image
            scratched_image = await self.image_repo.get_by_id(scratched_id, session)
            if not scratched_image:
                raise NotFoundError("ExperimentImage", scratched_id)

            if scratched_image.experiment_id != experiment_id:
                raise ServiceValidationError(
                    f"Image {scratched_id} does not belong to this experiment"
                )

            # Analyze scratched image with ROI (same coords for all images)
            scratched_analysis = self.analyze_image(
                scratched_image.image_data, rect_coords
            )

            # Calculate scratch index for this scratched image
            # Using pixel ratio (count_q / total_pixels) instead of absolute count
            scratch_index = self.calculate_scratch_index(
                scratched_analysis["histogram"], scratched_analysis["total_pixels"]
            )

            scratched_analyses.append(
                {
                    "image_id": str(scratched_id),
                    "passes": scratched_image.passes,
                    "analysis": scratched_analysis,
                    "scratch_index": scratch_index,
                }
            )

            scratch_indices.append(scratch_index)

        # Scratch index for reference image (same formula, no comparison).
        # Uses pixel ratio (count_q / total_pixels).
        reference_scratch_index = self.calculate_scratch_index(
            reference_analysis["histogram"], reference_analysis["total_pixels"]
        )

        # Include reference index in statistics
        scratch_indices.insert(0, reference_scratch_index)

        # Calculate summary statistics (includes reference image)
        avg_scratch_index = np.mean(scratch_indices) if scratch_indices else 0.0
        max_scratch_index = np.max(scratch_indices) if scratch_indices else 0.0
        min_scratch_index = np.min(scratch_indices) if scratch_indices else 0.0

        return {
            "experiment_id": str(experiment_id),
            "reference_image": {
                "image_id": str(reference_image_id),
                "passes": reference_image.passes,
                "analysis": reference_analysis,
                "scratch_index": reference_scratch_index,
            },
            "scratched_images": scratched_analyses,
            "summary": {
                "average_scratch_index": float(avg_scratch_index),
                "max_scratch_index": float(max_scratch_index),
                "min_scratch_index": float(min_scratch_index),
                "num_scratched_images": len(scratched_analyses),
            },
        }
