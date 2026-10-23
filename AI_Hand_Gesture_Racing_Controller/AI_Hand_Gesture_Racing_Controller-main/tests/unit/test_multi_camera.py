"""Camera persistence, hot switching, reconnect, and failover."""

from types import SimpleNamespace

from src.camera.camera_sources import CameraSource, MultiCameraManager
from src.exceptions import CameraError


class Registry:
    """In-memory camera state."""

    remembered: str | None = None

    def last_source_id(self) -> str | None:
        return self.remembered

    def remember(self, source_id: str) -> None:
        self.remembered = source_id


class FakeManager:
    """Deterministic capture manager."""

    def __init__(self, source_id: str, fails: bool = False) -> None:
        self.source_id = source_id
        self.fails = fails
        self.diagnostics = SimpleNamespace(backend="fake")
        self.released = False

    def read(self):
        if self.fails:
            raise CameraError("disconnected")
        return self.source_id

    def release(self) -> None:
        self.released = True


def test_hot_switch_remembers_source() -> None:
    sources = [
        CameraSource("one", "One", "local", 0),
        CameraSource("two", "Two", "obs", 1),
    ]
    registry = Registry()
    manager = MultiCameraManager(
        sources, lambda source: FakeManager(source.source_id), registry  # type: ignore[arg-type]
    )
    assert manager.switch_next().source_id == "two"
    assert manager.read() == "two"
    assert registry.remembered == "two"


def test_disconnect_fails_over() -> None:
    sources = [
        CameraSource("bad", "Bad", "local", 0),
        CameraSource("good", "Good", "local", 1),
    ]
    attempts = {"bad": 0}

    def factory(source: CameraSource) -> FakeManager:
        if source.source_id == "bad":
            attempts["bad"] += 1
            return FakeManager("bad", True)
        return FakeManager("good")

    manager = MultiCameraManager(
        sources, factory, Registry(), reconnect_attempts=1  # type: ignore[arg-type]
    )
    assert manager.read() == "good"
    assert manager.current_source.source_id == "good"
