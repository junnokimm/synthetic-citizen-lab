"""Experiment CLI for project, scenario, and question-set metadata."""

import json
import sys

from pydantic import ValidationError

from synthetic_citizen_lab._experiment_cli_actions import (
    _handle_init_project,
    _handle_run,
    _handle_save_questions,
    _handle_save_scenario,
    _handle_show,
)
from synthetic_citizen_lab._experiment_cli_args import (
    _ExperimentCliUsageError,
    _parse_init_project_args,
    _parse_save_question_set_args,
    _parse_save_scenario_args,
    _parse_show_args,
    _raise_usage,
)
from synthetic_citizen_lab._experiment_cli_run_args import _parse_run_args


def main(args: tuple[str, ...] | None = None) -> int:
    """Run the experiment metadata CLI."""
    argv = tuple(sys.argv[1:] if args is None else args)
    if not argv or argv[0] in {"-h", "--help"}:
        _print_help()
        return 0

    command = argv[0]
    command_args = argv[1:]
    if command_args == ("--help",):
        _print_command_help(command)
        return 0
    try:
        match command:
            case "init-project":
                _handle_init_project(_parse_init_project_args(command_args))
            case "save-scenario":
                _handle_save_scenario(_parse_save_scenario_args(command_args))
            case "save-questions":
                _handle_save_questions(_parse_save_question_set_args(command_args))
            case "show":
                _handle_show(_parse_show_args(command_args))
            case "run":
                _handle_run(_parse_run_args(command_args))
            case _:
                _raise_usage(f"Unsupported command: {command}")
    except (_ExperimentCliUsageError, ValidationError, FileNotFoundError) as error:
        sys.stderr.write(f"error: {error}\n")
        return 2
    return 0


def _print_help() -> None:
    commands = {
        "init-project": "Create a project artifact.",
        "save-scenario": "Save one scenario definition with A/B/C-like variants.",
        "save-questions": (
            "Save one question set with ORIGINAL and "
            "SAME_QUESTION_REPEAT questions."
        ),
        "show": "Print one saved project, scenario, or question set as JSON.",
        "run": "Execute one deterministic mock experiment run.",
    }
    sys.stdout.write(json.dumps(commands, ensure_ascii=False, indent=2) + "\n")


def _print_command_help(command: str) -> None:
    command_help = {
        "init-project": {
            "command": "init-project",
            "required": ["--project-id", "--name", "--research-goal", "--non-claim"],
            "optional": ["--output-dir"],
        },
        "save-scenario": {
            "command": "save-scenario",
            "required": ["--project-id", "--scenario-id", "--title", "--variant"],
            "optional": ["--output-dir"],
        },
        "save-questions": {
            "command": "save-questions",
            "required": ["--project-id", "--question-set-id", "--name", "--question"],
            "optional": ["--output-dir"],
        },
        "show": {
            "command": "show",
            "required": ["project|scenario|question-set", "--project-id"],
            "optional": ["--output-dir", "--scenario-id", "--question-set-id"],
        },
        "run": {
            "command": "run",
            "required": [
                "--cohort-dir",
                "--project-id",
                "--run-id",
                "--scenario-id",
                "--question-set-id",
                "--seed",
            ],
            "optional": [
                "--output-dir",
                "--persona-context-level",
                "--model",
                "--temperature",
                "--prompt-version",
            ],
        },
    }
    if command not in command_help:
        _raise_usage(f"Unsupported command: {command}")
    payload = json.dumps(command_help[command], ensure_ascii=False, indent=2)
    sys.stdout.write(payload + "\n")
