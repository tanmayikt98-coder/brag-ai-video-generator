"""End-to-end abstract dispatch tests for ML gesture actions."""

import logging

import pytest

from src.controller import CommandManager, KeyboardController
from src.gesture import Command
from src.ml import (
    GestureActionMapping,
    resolve_mapped_actions,
    select_pedal_command,
)


def _manager() -> tuple[CommandManager, KeyboardController]:
    keyboard = KeyboardController(dry_run=True)
    manager = CommandManager(
        keyboard,
        {"left": "left", "right": "right", "accelerate": "up", "brake": "down"},
    )
    return manager, keyboard


def test_closed_fist_accelerates_and_open_palm_brakes(caplog) -> None:
    caplog.set_level(logging.INFO)
    mapping = GestureActionMapping(
        {
            "open_palm": (Command.BRAKE,),
            "closed_fist": (Command.ACCELERATE,),
        }
    )
    manager, keyboard = _manager()
    open_actions = resolve_mapped_actions(mapping.commands_for("open_palm"))
    manager.apply(Command.STRAIGHT, open_actions.pedal, True)
    assert keyboard.active_keys == {"down"}
    fist_actions = resolve_mapped_actions(mapping.commands_for("closed_fist"))
    manager.apply(Command.STRAIGHT, fist_actions.pedal, True)
    assert keyboard.active_keys == {"up"}
    assert "DRY-RUN release down" in caplog.text
    assert "DRY-RUN press up" in caplog.text
    manager.shutdown()
    assert keyboard.active_keys == set()


def test_ml_mode_cannot_be_overwritten_by_rule_based_pedal() -> None:
    assert select_pedal_command(True, Command.IDLE, Command.ACCELERATE) is Command.IDLE
    assert select_pedal_command(False, Command.IDLE, Command.ACCELERATE) is Command.ACCELERATE


def test_conflicting_ml_pedal_mapping_is_rejected() -> None:
    with pytest.raises(ValueError, match="simultaneously"):
        resolve_mapped_actions({Command.ACCELERATE, Command.BRAKE})
