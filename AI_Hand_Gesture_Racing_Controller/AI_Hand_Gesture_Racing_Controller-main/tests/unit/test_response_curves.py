"""Continuous response-curve tests."""

import pytest

from src.gesture.response_curves import apply_response_curve


@pytest.mark.parametrize("curve", ["linear", "cubic", "exponential", "sigmoid"])
def test_curves_preserve_zero_sign_and_endpoints(curve: str) -> None:
    assert apply_response_curve(0, curve) == pytest.approx(0)
    assert apply_response_curve(1, curve) == pytest.approx(1)
    assert apply_response_curve(-1, curve) == pytest.approx(-1)
    assert apply_response_curve(-0.5, curve) < 0


def test_unknown_curve_rejected() -> None:
    with pytest.raises(ValueError):
        apply_response_curve(0.5, "unknown")
