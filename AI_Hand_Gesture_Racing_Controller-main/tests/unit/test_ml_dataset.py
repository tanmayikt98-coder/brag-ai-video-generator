"""Tests for gesture dataset quality controls."""

import json

import pytest

from src.ml import GestureDataset, GestureSample


def _sample(label: str, value: float) -> GestureSample:
    return GestureSample(label, (value, value + 0.1), "Right", 1.0)


def test_dataset_deduplicates_validates_and_exports(tmp_path) -> None:
    dataset = GestureDataset(tmp_path / "samples.jsonl", 2)
    assert dataset.append(_sample("open", 0.1))
    assert not dataset.append(_sample("open", 0.1))
    assert dataset.append(_sample("fist", 0.3))
    report = dataset.validate({"open": 2, "fist": 1})
    assert report.labels == {"open": 1, "fist": 1}
    assert report.missing_by_label == {"open": 1, "fist": 0}
    data_path, manifest_path = dataset.export(tmp_path / "export")
    assert data_path.exists()
    assert json.loads(manifest_path.read_text(encoding="utf-8"))["sample_count"] == 2


def test_dataset_rejects_invalid_features(tmp_path) -> None:
    dataset = GestureDataset(tmp_path / "samples.jsonl", 2)
    with pytest.raises(ValueError, match="finite"):
        dataset.append(_sample("open", float("nan")))
