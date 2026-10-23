"""Renderer state coverage without OpenCV, GUI, or hardware."""

from src.gesture import Command
from src.gesture.steering_detector import SteeringResult
from src.hand_tracking import HandRoleTracker, HandTrackingResult
from src.visualization.overlay_renderer import (
    OverlayRenderer,
    VisualizationSettings,
    build_hud_lines,
)
from tests.fixtures.sample_landmarks import make_hand, make_two_hands


class DummyFrame:
    """Minimal frame accepted while drawing functions are mocked."""

    shape = (720, 1280, 3)


def steering(valid: bool = False) -> SteeringResult:
    """Build an invalid or valid display state."""
    if not valid:
        return SteeringResult(Command.STRAIGHT, None, None, 0, 0, 0, False, 0, reason="lost")
    return SteeringResult(Command.STRAIGHT, 0, 0, 0, 0, 0.4, True, 0.9, reason="live")


def test_renderer_handles_zero_one_stale_two_and_invalid(monkeypatch) -> None:
    monkeypatch.setattr("src.visualization.overlay_renderer.draw_landmarks", lambda *args: None)
    monkeypatch.setattr("src.visualization.overlay_renderer.draw_steering", lambda *args: None)
    monkeypatch.setattr("src.visualization.overlay_renderer.draw_status", lambda *args: None)
    monkeypatch.setattr(OverlayRenderer, "_draw_confidence", lambda *args: None)
    renderer = OverlayRenderer()
    tracker = HandRoleTracker(persistence_frames=2, persistence_ms=1000)
    two = make_two_hands()
    live_roles = tracker.update(two)
    stale_roles = tracker.update(HandTrackingResult((make_hand("Left", 0.3, 0.5),), 0.1))
    cases = (
        (HandTrackingResult(), None, steering()),
        (HandTrackingResult((make_hand("Left", 0.3, 0.5),)), None, steering()),
        (HandTrackingResult((make_hand("Left", 0.3, 0.5),)), stale_roles, steering(True)),
        (two, live_roles, steering(True)),
        (two, live_roles, steering()),
    )
    for hands, roles, state in cases:
        assert (
            renderer.render(
                DummyFrame(),
                hands,
                state,
                Command.IDLE,
                None,
                set(),
                True,
                False,
                False,
                roles,
                None,
            ).shape
            == DummyFrame.shape
        )


def test_hud_handles_missing_diagnostics() -> None:
    lines = build_hud_lines(
        HandTrackingResult(),
        None,
        steering(),
        Command.IDLE,
        None,
        None,
        VisualizationSettings(),
    )
    assert any("unavailable" in line for line in lines)
    assert any("Tracking: LOST" in line for line in lines)
