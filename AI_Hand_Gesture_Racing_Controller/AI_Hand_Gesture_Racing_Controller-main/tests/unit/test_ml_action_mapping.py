"""Tests for editable abstract action mappings."""

from pathlib import Path

import pytest

from src.gesture import Command
from src.ml import GestureActionMapping


def test_action_mapping_round_trip(tmp_path) -> None:
    path = tmp_path / "mapping.yaml"
    mapping = GestureActionMapping()
    mapping.set("open_palm", {Command.BRAKE, Command.NITRO})
    mapping.save(path)
    loaded = GestureActionMapping.load(path)
    assert loaded.commands_for("open_palm") == {Command.BRAKE, Command.NITRO}
    assert loaded.commands_for("unknown") == set()


def test_action_mapping_rejects_unknown_command(tmp_path) -> None:
    path = tmp_path / "mapping.yaml"
    path.write_text("mappings:\n  wave: [teleport]\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid action mapping"):
        GestureActionMapping.load(path)


def test_project_mapping_has_locked_pedal_meanings() -> None:
    mapping = GestureActionMapping.load(Path("config/gesture_actions.yaml"))
    assert mapping.commands_for("closed_fist") == {Command.ACCELERATE}
    assert mapping.commands_for("open_palm") == {Command.BRAKE}
