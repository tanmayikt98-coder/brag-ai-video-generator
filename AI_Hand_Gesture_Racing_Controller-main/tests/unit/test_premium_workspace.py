"""Focused tests for the integrated preview and game workspace."""

from pathlib import Path

import numpy as np
import pytest

from src.diagnostics import export_diagnostics
from src.game_integration import (
    BrowserWorkspaceManager,
    select_integration_mode,
    validate_game_url,
)
from src.gui.preview import aspect_fit_size, bgr_frame_to_qimage
from src.utils.config_manager import ConfigurationManager
from src.utils.file_handler import load_json
from src.utils.user_settings import UserSettings, UserSettingsStore


def test_aspect_fit_preserves_16_by_9() -> None:
    assert aspect_fit_size(1280, 720, 800, 800) == (800, 450)
    assert aspect_fit_size(1280, 720, 400, 180) == (320, 180)


def test_v2_camera_and_layout_defaults() -> None:
    config = ConfigurationManager().load(
        Path("config/default_config.yaml"), generate_if_missing=False
    )
    assert (config["camera"]["requested_width"], config["camera"]["requested_height"]) == (
        1280,
        720,
    )
    assert config["ui"]["integrated_preview"] is True
    assert config["ui"]["camera_aspect_ratio"] == "16:9"
    assert config["ui"]["default_layout"] == "studio"
    assert config["game"]["integration_mode"] == "auto"


def test_frame_conversion_owns_rgb_image_data() -> None:
    frame = np.zeros((2, 3, 3), dtype=np.uint8)
    frame[0, 0] = (1, 2, 3)
    image = bgr_frame_to_qimage(frame)
    frame[:] = 255
    assert (image.width(), image.height()) == (3, 2)
    assert image.pixelColor(0, 0).getRgb()[:3] == (3, 2, 1)


def test_dashboard_exposes_integrated_preview_and_controls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication, QPushButton

    from src.gui.dashboard import create_dashboard_class

    app = QApplication.instance() or QApplication([])
    dashboard = create_dashboard_class()("studio")
    dashboard.resize(1200, 720)
    dashboard.show()
    app.processEvents()
    labels = {button.text() for button in dashboard.findChildren(QPushButton)}
    assert dashboard.preview.isVisible()
    assert {"Launch Game", "Arrange Windows", "EMERGENCY STOP"} <= labels
    dashboard.close()


@pytest.mark.parametrize("window_size", [(1366, 768), (1920, 1080)])
def test_studio_layout_is_balanced_and_camera_is_16_by_9(
    monkeypatch: pytest.MonkeyPatch,
    window_size: tuple[int, int],
) -> None:
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication, QLabel

    from src.gui.dashboard import create_dashboard_class

    app = QApplication.instance() or QApplication([])
    dashboard = create_dashboard_class()("studio")
    dashboard.resize(*window_size)
    dashboard.show()
    app.processEvents()

    camera_width, game_width = dashboard.splitter.sizes()
    camera_ratio = camera_width / (camera_width + game_width)
    assert camera_ratio == pytest.approx(0.41, abs=0.025)
    assert dashboard.camera_card.height() == dashboard.game_card.height()
    assert dashboard.camera_card.y() == dashboard.game_card.y()
    assert dashboard.preview.width() / dashboard.preview.height() == pytest.approx(16 / 9, abs=0.04)

    camera_text = {
        label.text()
        for label in dashboard.camera_card.findChildren(QLabel)
        if label is not dashboard.preview and label is not dashboard.preview.mode_badge
    }
    assert camera_text == {"CAMERA & HAND TRACKING"}
    dashboard.close()


def test_preview_uses_compact_safety_badge(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from src.gui.preview import create_camera_preview_class

    app = QApplication.instance() or QApplication([])
    preview = create_camera_preview_class()()
    preview.resize(640, 360)
    preview.set_mode("TEST")
    app.processEvents()
    assert preview.mode_badge.text() == "TEST · NO KEY OUTPUT"
    assert preview.mode_badge.height() < 40
    preview.set_mode("LIVE")
    assert preview.mode_badge.text() == "LIVE · KEYS ENABLED"


def test_invalid_frame_conversion_is_readable() -> None:
    with pytest.raises(ValueError, match="BGR image"):
        bgr_frame_to_qimage(np.zeros((3, 3), dtype=np.uint8))


def test_game_url_and_integration_fallback() -> None:
    assert validate_game_url("https://www.crazygames.com/game/racing-limits")
    with pytest.raises(ValueError, match="absolute"):
        validate_game_url("javascript:alert(1)")
    decision = select_integration_mode("auto", webengine=True)
    assert decision.mode == "external"
    assert "WebGL" in decision.reason
    assert select_integration_mode("embedded", webengine=False).mode == "external"


class FakeWindows:
    def __init__(self) -> None:
        self.arranged: tuple[int, int] | None = None
        self.focused: int | None = None

    def find_window(self, _title: str) -> int | None:
        return 22

    def arrange_side_by_side(self, dashboard: int, game: int) -> bool:
        self.arranged = (dashboard, game)
        return True

    def focus(self, handle: int) -> bool:
        self.focused = handle
        return True


def test_external_workspace_launch_arrange_and_focus() -> None:
    backend = FakeWindows()
    opened: list[str] = []
    manager = BrowserWorkspaceManager(
        "https://example.com/game",
        "Example",
        backend=backend,
        opener=lambda url: not opened.append(url),
    )
    assert "launched" in manager.launch()
    assert opened == ["https://example.com/game"]
    assert "side by side" in manager.arrange(11)
    assert backend.arranged == (11, 22)
    assert manager.focus_game() == "Game focused"
    assert backend.focused == 22


def test_user_layout_and_geometry_persist(tmp_path: Path) -> None:
    store = UserSettingsStore(tmp_path / "settings.json")
    store.save(UserSettings(layout_mode="compact", window_geometry="Z2VvbWV0cnk="))
    loaded = store.load()
    assert loaded.layout_mode == "compact"
    assert loaded.window_geometry == "Z2VvbWV0cnk="


def test_diagnostics_include_integrated_workspace_context(tmp_path: Path) -> None:
    output = export_diagnostics(
        tmp_path / "diagnostics.json",
        runtime_context={
            "preview_rendering_mode": "integrated_qt",
            "selected_layout_mode": "studio",
            "game_integration_mode": "external",
        },
    )
    report = load_json(output)
    assert isinstance(report["system"]["frozen"], bool)
    assert report["runtime"]["preview_rendering_mode"] == "integrated_qt"
    assert report["runtime"]["game_integration_mode"] == "external"


def test_packaging_collects_dynamic_preview_modules() -> None:
    spec = Path("packaging/controller.spec").read_text(encoding="utf-8")
    assert '"src.gui.dashboard"' in spec
    assert '"src.gui.preview"' in spec
