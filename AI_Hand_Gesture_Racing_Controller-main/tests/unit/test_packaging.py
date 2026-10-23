"""Release-build asset validation."""

from pathlib import Path


def test_packaging_definitions_exist_and_reference_plugins() -> None:
    spec = Path("packaging/controller.spec").read_text(encoding="utf-8")
    installer = Path("packaging/installer.iss").read_text(encoding="utf-8")
    assert 'project_root / "plugins"' in spec
    assert '"models/trained"' in spec
    assert 'project_root / "gui.py"' in spec
    assert 'collect_submodules("qtwebview2")' in spec
    assert 'collect_data_files("qtwebview2", includes=["lib/**"])' in spec
    assert 'collect_dynamic_libs("qtwebview2")' in spec
    assert '(str(Path(qtwebview2_package) / "lib"), "lib")' in spec
    assert '"PySide6.QtWebEngineWidgets"' in spec
    assert "AppVersion=2.0.0.dev0" in installer
    assert "AIHandGestureRacingController.exe" in installer
