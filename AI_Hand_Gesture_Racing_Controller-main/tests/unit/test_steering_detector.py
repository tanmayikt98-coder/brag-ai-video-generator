"""Version 2 wheel geometry, filtering, and hysteresis tests."""

from src.gesture import Command
from src.gesture.steering_detector import SteeringDetector
from src.hand_tracking import Point2D, SteeringHands, TrackedHand
from tests.fixtures.sample_landmarks import make_hand


def pair(left: Point2D | None = None, right: Point2D | None = None) -> SteeringHands:
    """Build role state at precise reference points."""
    left = left or Point2D(0.3, 0.5)
    right = right or Point2D(0.7, 0.5)
    left_hand, right_hand = make_hand("Right", left.x, left.y), make_hand("Left", right.x, right.y)
    return SteeringHands(
        TrackedHand("steering_left", left_hand, left, left, 1, 1.0, confidence=0.9),
        TrackedHand("steering_right", right_hand, right, right, 1, 1.0, confidence=0.8),
    )


def test_raw_angle_neutral_offset_and_inversion() -> None:
    result = SteeringDetector(angle_smoothing_alpha=1, median_window=1).detect(
        pair(right=Point2D(0.7, 0.6))
    )
    assert result.raw_angle_degrees is not None
    offset = SteeringDetector(
        neutral_angle=result.raw_angle_degrees, angle_smoothing_alpha=1, median_window=1
    ).detect(pair(right=Point2D(0.7, 0.6)))
    assert offset.calibrated_angle_degrees == 0
    inverted = SteeringDetector(invert=True, angle_smoothing_alpha=1, median_window=1).detect(
        pair(right=Point2D(0.7, 0.6))
    )
    assert inverted.calibrated_angle_degrees == -result.calibrated_angle_degrees


def test_span_and_invalid_hands_neutralize() -> None:
    detector = SteeringDetector()
    assert not detector.detect(pair(Point2D(0.48, 0.5), Point2D(0.52, 0.5))).valid
    empty = detector.detect(SteeringHands(None, None))
    assert empty.command is Command.STRAIGHT
    assert not empty.valid


def test_angle_jump_is_rejected() -> None:
    detector = SteeringDetector(max_angle_jump=10, angle_smoothing_alpha=1, median_window=1)
    assert detector.detect(pair()).valid
    assert not detector.detect(pair(right=Point2D(0.7, 0.7))).valid


def test_left_and_right_hysteresis_state_machine() -> None:
    detector = SteeringDetector()
    assert detector.command_for_angle(-13) is Command.LEFT
    assert detector.command_for_angle(-8) is Command.LEFT
    assert detector.command_for_angle(-6) is Command.STRAIGHT
    assert detector.command_for_angle(13) is Command.RIGHT
    assert detector.command_for_angle(8) is Command.RIGHT
    assert detector.command_for_angle(6) is Command.STRAIGHT
