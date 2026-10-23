"""Session telemetry recording without video codecs."""

import json

from src.gesture import Command
from src.gesture.steering_detector import SteeringResult
from src.recording.session_recorder import SessionRecorder


def test_session_writes_metadata_and_telemetry(tmp_path, monkeypatch) -> None:
    recorder = SessionRecorder(tmp_path, "mp4v", 30)
    video_path = recorder.directory / "video.mp4"
    monkeypatch.setattr(recorder.video, "start", lambda size: video_path)
    monkeypatch.setattr(recorder.video, "write", lambda frame: None)
    monkeypatch.setattr(recorder.video, "stop", lambda: None)
    paths = recorder.start((640, 480), "Normal", "calibration.yaml", {"backend": "dshow"})
    steering = SteeringResult(
        Command.LEFT, -20, -20, -18, -0.4, 0.4, True, 0.8, profile_name="Normal"
    )
    recorder.write(object(), 1.25, steering, Command.ACCELERATE)
    recorder.stop()
    metadata = json.loads(paths.metadata.read_text(encoding="utf-8"))
    telemetry = json.loads(paths.telemetry.read_text(encoding="utf-8").strip())
    assert metadata["profile"] == "Normal"
    assert telemetry["confidence"] == 0.8
    assert telemetry["command"] == "left"
