"""Tests for invariant, model-ready hand features."""

import math

import pytest

from src.hand_tracking import DetectedHand, HandLandmarks, Point2D
from src.ml import HandFeatureExtractor


def _hand(offset_x: float = 0.0, scale: float = 1.0) -> DetectedHand:
    normalized = tuple(
        Point2D(offset_x + scale * (index % 5) * 0.03, 0.2 + scale * (index // 5) * 0.04)
        for index in range(21)
    )
    return DetectedHand("Right", 0.98, HandLandmarks(normalized, normalized))


def test_features_are_fixed_finite_and_translation_invariant() -> None:
    extractor = HandFeatureExtractor()
    original = extractor.extract(_hand()).values
    translated = extractor.extract(_hand(0.3)).values
    assert len(original) == extractor.feature_count == 70
    assert all(math.isfinite(value) for value in original)
    assert translated == pytest.approx(original)


def test_features_reject_incomplete_landmarks() -> None:
    points = tuple(Point2D(0.0, 0.0) for _ in range(20))
    with pytest.raises(ValueError, match="Expected 21"):
        HandFeatureExtractor().extract(DetectedHand("Right", 1.0, HandLandmarks(points, points)))
