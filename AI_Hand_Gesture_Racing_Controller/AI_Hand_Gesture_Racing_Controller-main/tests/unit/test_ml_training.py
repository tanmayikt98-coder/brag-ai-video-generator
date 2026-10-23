"""Fast validation tests for the training boundary."""

import pytest

from src.ml import GestureDataset, GestureModelTrainer, GestureSample


def test_training_rejects_single_class_before_loading_ml_dependencies(tmp_path) -> None:
    dataset = GestureDataset(tmp_path / "samples.jsonl", 2)
    dataset.append(GestureSample("open", (0.1, 0.2), "Right", 1.0))
    with pytest.raises(ValueError, match="at least two"):
        GestureModelTrainer().train(dataset, tmp_path / "model")
