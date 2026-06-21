"""Math invariants for ImageAnalysisService.

These are pure functions (no DB / IO), so we can pin the formula behaviour
that drives the entire scratch-resistance product without spinning up
infrastructure.
"""

from __future__ import annotations

import numpy as np

from src.repositories.experiment_repository import ExperimentRepository
from src.repositories.image_repository import ExperimentImageRepository
from src.services.image_analysis_service import ImageAnalysisService


def _service() -> ImageAnalysisService:
    # The repos aren't touched by the pure-math methods we test here;
    # we still need real instances for the constructor signature.
    return ImageAnalysisService(
        image_repository=ExperimentImageRepository(),
        experiment_repository=ExperimentRepository(),
    )


def test_scratch_index_pure_black_is_zero():
    """Pure-black image (all pixels at brightness 0) ⇒ index = 0."""
    svc = _service()
    hist = {0: 1000}
    index = svc.calculate_scratch_index(hist, total_pixels=1000)
    assert index == 0.0


def test_scratch_index_pure_white_is_one():
    """Pure-white (brightness 255) ⇒ index = 1.0 ( = 255/255 )."""
    svc = _service()
    hist = {255: 1000}
    index = svc.calculate_scratch_index(hist, total_pixels=1000)
    assert abs(index - 1.0) < 1e-9


def test_scratch_index_uniform_grey():
    """50% grey (brightness 128) ⇒ index = 0.502 ( = round(128/255, 3) )."""
    svc = _service()
    hist = {128: 1000}
    index = svc.calculate_scratch_index(hist, total_pixels=1000)
    assert index == round(128 / 255, 3) == 0.502


def test_scratch_index_rounded_to_3_decimals():
    """The index is always rounded to 3 decimals at the source."""
    svc = _service()
    # Mixed levels produce a long fractional value; it must come back at 3dp.
    hist = {10: 333, 137: 333, 251: 334}
    index = svc.calculate_scratch_index(hist, total_pixels=1000)
    assert index == round(index, 3)


def test_scratch_index_total_pixels_zero_is_zero():
    """Edge case: defensive guard — never divide by zero."""
    svc = _service()
    assert svc.calculate_scratch_index({0: 1, 100: 5}, total_pixels=0) == 0.0


def test_grayscale_rejects_non_rgb():
    import pytest

    from src.services.exceptions import ValidationError as ServiceValidationError

    svc = _service()
    grayscale_input = np.zeros((10, 10), dtype=np.uint8)  # 2D, not (H, W, 3)
    with pytest.raises(ServiceValidationError):
        svc.convert_to_grayscale(grayscale_input)


def test_grayscale_pure_red_yields_77():
    """0.3 * 255 + 0.59 * 0 + 0.11 * 0 = 76.5 → uint8 truncates to 76."""
    svc = _service()
    red = np.zeros((5, 5, 3), dtype=np.uint8)
    red[:, :, 0] = 255
    out = svc.convert_to_grayscale(red)
    assert out.shape == (5, 5)
    assert out.dtype == np.uint8
    assert int(out[0, 0]) == 76  # floor(0.3 * 255)


def test_calculate_histogram_skips_empty_bins():
    """Empty bins (count = 0) are NOT stored — saves JSON size in scratch_results."""
    svc = _service()
    img = np.array([[10, 10, 200]], dtype=np.uint8)
    hist = svc.calculate_histogram(img)
    assert hist == {10: 2, 200: 1}
