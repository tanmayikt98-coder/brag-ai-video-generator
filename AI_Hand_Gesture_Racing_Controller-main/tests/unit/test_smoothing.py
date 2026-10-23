"""Smoothing and stabilization behavior."""

import pytest

from src.smoothing import CommandStabilizer, ExponentialSmoother, MovingAverage


def test_moving_and_exponential_average() -> None:
    average = MovingAverage(2)
    assert average.update(2) == 2
    assert average.update(4) == 3
    smoother = ExponentialSmoother(0.5)
    assert smoother.update(10) == 10
    assert smoother.update(20) == 15


def test_invalid_parameters_and_debounce() -> None:
    with pytest.raises(ValueError):
        MovingAverage(0)
    with pytest.raises(ValueError):
        ExponentialSmoother(0)
    stabilizer = CommandStabilizer(2, "idle")
    assert stabilizer.update("go") == "idle"
    assert stabilizer.update("go") == "go"
