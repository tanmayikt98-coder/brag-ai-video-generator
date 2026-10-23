"""One Euro adaptive filter behavior."""

import pytest

from src.hand_tracking import Point2D
from src.smoothing.one_euro_filter import (
    OneEuroAngleFilter,
    OneEuroFilter,
    OneEuroPointFilter,
)


def test_constant_signal_stabilizes_and_fast_motion_adapts() -> None:
    filter_ = OneEuroFilter(min_cutoff=0.5, beta=0.2, frequency=100)
    assert filter_.update(0, 0.0) == 0
    slow = filter_.update(0.01, 0.01)
    fast = filter_.update(1.0, 0.02)
    assert 0 < slow < 0.01
    assert fast > slow


def test_point_and_angle_filters() -> None:
    point_filter = OneEuroPointFilter.create(frequency=30)
    assert point_filter.update(Point2D(0.2, 0.3), 0) == Point2D(0.2, 0.3)
    angle_filter = OneEuroAngleFilter(frequency=30)
    angle_filter.update(179, 0)
    assert abs(angle_filter.update(-179, 1 / 30)) > 170


def test_invalid_filter_parameters() -> None:
    with pytest.raises(ValueError):
        OneEuroFilter(min_cutoff=0)
