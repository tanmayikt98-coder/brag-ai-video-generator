"""Final-release persistence, safety, profile, and diagnostics tests."""

import json
import sys
from pathlib import Path

import pytest

from src import __version__
from src.controller.key_mapping import validate_mapping
from src.exceptions import InvalidKeyMappingError
from src.game_profiles import ConfiguredGameProfile, GameManager, ProfileStore
from src.gesture import Command
from src.ml import GestureActionMapping
from src.utils.resources import editable_config_path, resource_path
from src.utils.user_settings import UserSettings, UserSettingsStore


def profile(profile_id: str = "test_game") -> ConfiguredGameProfile:
    """Create a valid test profile."""
    return ConfiguredGameProfile(
        profile_id=profile_id,
        name="Test Game",
        platform="Windows",
        key_mapping={"accelerate": "w", "brake": "s", "left": "a", "right": "d"},
        sensitivity_profile="normal",
    )


def test_user_settings_persist_and_default_to_safe_test_mode(tmp_path: Path) -> None:
    store = UserSettingsStore(tmp_path / "settings.json")
    defaults = store.load()
    assert defaults.test_mode
    assert defaults.selected_profile_id == "generic_wasd"
    defaults.first_run_completed = True
    defaults.theme = "Blue"
    store.save(defaults)
    assert store.load() == defaults


def test_invalid_user_settings_are_readable(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    path.write_text('{"selected_profile_id": ""}', encoding="utf-8")
    with pytest.raises(ValueError, match="selected_profile_id"):
        UserSettingsStore(path).load()


def test_profile_store_crud_import_and_export(tmp_path: Path) -> None:
    store = ProfileStore(tmp_path / "profiles")
    stored = store.save(profile())
    assert store.list()["test_game"].key_mapping["accelerate"] == "w"
    duplicate = store.duplicate("test_game", "test_copy", "Test Copy")
    exported = store.export_profile("test_copy", tmp_path / "export.yaml")
    imported_store = ProfileStore(tmp_path / "imported")
    imported_store.import_profile(exported)
    assert stored.exists() and duplicate.exists()
    assert "test_copy" in imported_store.list()
    store.delete("test_game")
    assert "test_game" not in store.list()


def test_conflicting_keyboard_mappings_are_rejected() -> None:
    with pytest.raises(InvalidKeyMappingError, match="accelerate and brake"):
        validate_mapping({"accelerate": "w", "brake": "w", "left": "a", "right": "d"})


def test_conflicting_gesture_actions_are_rejected() -> None:
    with pytest.raises(ValueError, match="both accelerate and brake"):
        GestureActionMapping.from_mapping({"mappings": {"open_palm": ["accelerate", "brake"]}})


def test_locked_mapping_has_no_stale_reversal() -> None:
    mapping = GestureActionMapping.load(Path("config/gesture_actions.yaml"))
    assert mapping.commands_for("closed_fist") == {Command.ACCELERATE}
    assert mapping.commands_for("open_palm") == {Command.BRAKE}


def test_generic_profiles_are_bundled() -> None:
    profiles = GameManager().discover()
    assert profiles["generic_wasd"].key_mapping["accelerate"] == "w"
    assert profiles["generic_arrows"].key_mapping["accelerate"] == "up"


def test_packaged_resource_path_uses_meipass(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "_MEIPASS", "C:/bundle", raising=False)
    assert resource_path("config/default_config.yaml") == Path(
        "C:/bundle/config/default_config.yaml"
    )


def test_editable_config_is_copied_to_user_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source_root = tmp_path / "bundle"
    (source_root / "config").mkdir(parents=True)
    (source_root / "config" / "mapping.yaml").write_text("value: 1\n", encoding="utf-8")
    monkeypatch.setattr(sys, "_MEIPASS", str(source_root), raising=False)
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "local"))
    editable = editable_config_path("mapping.yaml")
    assert editable.read_text(encoding="utf-8") == "value: 1\n"


def test_version_is_consistent_with_configuration() -> None:
    import yaml

    config = yaml.safe_load(Path("config/default_config.yaml").read_text(encoding="utf-8"))
    project = Path("pyproject.toml").read_text(encoding="utf-8")
    assert config["application"]["version"] == __version__
    assert f'version = "{__version__}"' in project


def test_settings_serialization_contains_no_project_write_requirement(tmp_path: Path) -> None:
    store = UserSettingsStore(tmp_path / "user" / "settings.json")
    store.save(UserSettings())
    assert json.loads(store.path.read_text(encoding="utf-8"))["test_mode"] is True
