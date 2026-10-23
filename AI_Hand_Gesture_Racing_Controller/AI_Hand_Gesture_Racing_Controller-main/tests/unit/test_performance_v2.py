"""Rolling per-stage performance metrics."""

from src.performance import PerformanceMonitor


def test_rolling_stage_metrics(monkeypatch) -> None:
    times = iter([0.0, 0.1, 0.2])
    monkeypatch.setattr(
        "src.performance.performance_monitor.time.perf_counter", lambda: next(times)
    )
    monitor = PerformanceMonitor(window=2)
    first = monitor.update(0.0, {"capture": 0.01, "inference": 0.02, "hand_processing": 0.003})
    second = monitor.update(0.1, {"capture": 0.03, "inference": 0.04, "hand_processing": 0.005})
    assert first.capture_ms == 10
    assert second.capture_ms == 20
    assert second.inference_ms == 30
    assert second.processing_ms == 4
