"""Replay cleanup with a mocked OpenCV backend."""

import json
from types import SimpleNamespace

from src.recording.replay import replay_session


def test_replay_releases_capture(tmp_path, monkeypatch) -> None:
    (tmp_path / "metadata.json").write_text(json.dumps({"video": "video.mp4"}), encoding="utf-8")
    calls: list[str] = []
    capture = SimpleNamespace(
        isOpened=lambda: True,
        get=lambda prop: 30,
        read=lambda: (False, None),
        release=lambda: calls.append("release"),
    )
    fake_cv2 = SimpleNamespace(
        VideoCapture=lambda path: capture,
        CAP_PROP_FPS=5,
        destroyAllWindows=lambda: calls.append("windows"),
    )
    monkeypatch.setitem(__import__("sys").modules, "cv2", fake_cv2)
    assert replay_session(tmp_path) == 0
    assert calls == ["release", "windows"]
