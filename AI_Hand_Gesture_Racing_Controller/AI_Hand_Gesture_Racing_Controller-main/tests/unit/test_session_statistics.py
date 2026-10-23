"""Constant-memory session report aggregation."""

from src.performance import SessionStatistics


def test_session_statistics_include_required_metrics() -> None:
    stats = SessionStatistics.create()
    stats.update(60, 0.9, -0.5, True)
    stats.update(50, 0.7, 0.5, False)
    report = stats.report(2.0, {"backend": "dshow"}, "Normal")
    assert report["average_fps"] == 55
    assert report["minimum_fps"] == 50
    assert report["tracking_loss_count"] == 1
    assert report["average_confidence"] == 0.8
    assert report["steering_variance"] == 0.25
