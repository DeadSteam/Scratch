"""S1 regression tests: ExperimentUpdate/Create must NOT accept user_id
or scratch_results from the client.

Both fields are server-set and would otherwise allow:
  * impersonation (reassigning ownership)
  * fabrication of scratch analysis results
"""

from __future__ import annotations

from uuid import uuid4

from src.schemas.experiment import ExperimentCreate, ExperimentUpdate


def test_experiment_update_ignores_user_id():
    """A user_id key in the JSON body is silently dropped (extra='ignore')."""
    update = ExperimentUpdate.model_validate(
        {
            "name": "renamed",
            "user_id": str(uuid4()),  # attacker tries to reassign ownership
        }
    )
    assert not hasattr(update, "user_id")
    # And the dumped payload also has no user_id.
    assert "user_id" not in update.model_dump(exclude_unset=True)


def test_experiment_update_ignores_scratch_results():
    """scratch_results is set only by ImageAnalysisService."""
    update = ExperimentUpdate.model_validate(
        {
            "name": "renamed",
            "scratch_results": [{"image_id": str(uuid4()), "scratch_index": 0.0}],
        }
    )
    assert not hasattr(update, "scratch_results")
    assert "scratch_results" not in update.model_dump(exclude_unset=True)


def test_experiment_create_does_not_accept_user_id():
    """Creator's user_id is injected from current_user, not from the payload."""
    create = ExperimentCreate.model_validate(
        {
            "film_id": str(uuid4()),
            "config_id": str(uuid4()),
            "user_id": str(uuid4()),  # ignored
            "weight": 12.5,
        }
    )
    assert not hasattr(create, "user_id")


def test_experiment_create_does_not_accept_scratch_results():
    create = ExperimentCreate.model_validate(
        {
            "film_id": str(uuid4()),
            "config_id": str(uuid4()),
            "scratch_results": [{"image_id": str(uuid4()), "scratch_index": 0.5}],
        }
    )
    assert not hasattr(create, "scratch_results")


def test_experiment_update_rect_coords_validation():
    """ROI must have 4 non-negative numbers."""
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        ExperimentUpdate.model_validate({"rect_coords": [1, 2, 3]})  # only 3
    with pytest.raises(ValidationError):
        ExperimentUpdate.model_validate({"rect_coords": [-1, 0, 10, 10]})  # negative
    # 4 non-negative ints accepted
    ok = ExperimentUpdate.model_validate({"rect_coords": [0, 0, 100, 100]})
    assert ok.rect_coords == [0, 0, 100, 100]
