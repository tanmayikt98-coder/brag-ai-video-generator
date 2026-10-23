"""Tests for confidence rejection and stable real-time predictions."""

from collections import deque
from pathlib import Path

from src.ml import (
    GestureInferenceEngine,
    HandFeatureExtractor,
    load_engine_or_none,
    resolve_model_path,
)
from tests.unit.test_ml_features import _hand


class _Model:
    classes_ = ("closed_fist", "open_palm")

    def __init__(self, probabilities: tuple[float, float]) -> None:
        self.probabilities = probabilities

    def predict_proba(self, features: object) -> list[tuple[float, float]]:
        del features
        return [self.probabilities]


def _engine(probabilities: tuple[float, float]) -> GestureInferenceEngine:
    engine = GestureInferenceEngine.__new__(GestureInferenceEngine)
    engine.extractor = HandFeatureExtractor()
    engine.model = _Model(probabilities)
    engine.threshold = 0.65
    engine.unknown_label = "unknown"
    engine.history = deque(maxlen=3)
    engine.stable_label = "unknown"
    return engine


def test_inference_accepts_confident_prediction() -> None:
    engine = _engine((0.1, 0.9))
    engine.predict(_hand())
    engine.predict(_hand())
    prediction = engine.predict(_hand())
    assert prediction.label == "open_palm"
    assert prediction.confidence == 0.9
    assert prediction.known


def test_inference_rejects_low_confidence_and_resets_history() -> None:
    engine = _engine((0.4, 0.6))
    prediction = engine.predict(_hand())
    assert prediction.label == "unknown"
    assert not prediction.known
    engine.reset()
    assert not engine.history
    assert engine.stable_label == "unknown"


def test_single_frame_label_change_does_not_replace_stable_prediction() -> None:
    engine = _engine((0.1, 0.9))
    for _ in range(3):
        prediction = engine.predict(_hand())
    assert prediction.label == "open_palm"
    engine.model = _Model((0.9, 0.1))
    assert engine.predict(_hand()).label == "open_palm"


def test_training_and_runtime_feature_transformations_are_identical() -> None:
    hand = _hand()
    training_features = HandFeatureExtractor().extract(hand).values
    assert _engine((0.1, 0.9)).extract_features(hand) == training_features


def test_relative_model_path_resolves_from_project_root(tmp_path) -> None:
    assert (
        resolve_model_path(Path("models/model.joblib"), tmp_path)
        == (tmp_path / "models/model.joblib").resolve()
    )


def test_model_loading_failure_is_reported(caplog, tmp_path) -> None:
    caplog.set_level("ERROR")
    engine = load_engine_or_none(
        model_path=tmp_path / "missing.joblib",
        metadata_path=tmp_path / "missing.json",
    )
    assert engine is None
    assert "ML model loading failed" in caplog.text
