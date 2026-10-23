"""Sensitivity profile loading and hot application."""

from pathlib import Path

from src.gesture.steering_detector import SteeringDetector
from src.gesture.steering_profiles import load_steering_profiles


def test_profiles_load_and_hot_switch() -> None:
    profiles = load_steering_profiles(Path("config/steering_profiles.yaml"))
    assert set(profiles) == {"easy", "normal", "pro"}
    detector = SteeringDetector()
    detector.apply_profile(profiles["pro"])
    assert detector.profile_name == "Pro"
    assert detector.response_curve == "sigmoid"
    assert detector.exit_right == profiles["pro"].dead_zone
