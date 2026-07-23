"""Run-command parsing for the experiment CLI."""

from dataclasses import dataclass
from pathlib import Path
from typing import Final

from synthetic_citizen_lab._experiment_cli_args import (
    DEFAULT_OUTPUT_DIR,
    _ExperimentCliUsageError,
    _parse_option_map,
    _required_option,
)
from synthetic_citizen_lab.experiments.context_models import PersonaContextLevel

_RUN_OPTIONS: Final[frozenset[str]] = frozenset(
    {
        "--cohort-dir",
        "--output-dir",
        "--project-id",
        "--run-id",
        "--scenario-id",
        "--question-set-id",
        "--persona-context-level",
        "--model",
        "--temperature",
        "--prompt-version",
        "--seed",
    }
)


@dataclass(frozen=True, slots=True)
class _RunArgs:
    cohort_dir: Path
    output_dir: Path
    project_id: str
    run_id: str
    scenario_id: str
    question_set_id: str
    persona_context_level: PersonaContextLevel
    model: str
    temperature: float
    prompt_version: str
    seed: int


def _parse_run_args(argv: tuple[str, ...]) -> _RunArgs:
    option_map = _parse_option_map(argv, allowed_options=_RUN_OPTIONS)
    return _RunArgs(
        cohort_dir=Path(_required_option(option_map, "--cohort-dir")),
        output_dir=Path(option_map.get("--output-dir", str(DEFAULT_OUTPUT_DIR))),
        project_id=_required_option(option_map, "--project-id"),
        run_id=_required_option(option_map, "--run-id"),
        scenario_id=_required_option(option_map, "--scenario-id"),
        question_set_id=_required_option(option_map, "--question-set-id"),
        persona_context_level=_parse_context_level(
            _string_option(
                option_map,
                "--persona-context-level",
                PersonaContextLevel.P2.value,
            )
        ),
        model=_string_option(option_map, "--model", "mock-model"),
        temperature=float(_string_option(option_map, "--temperature", "0.3")),
        prompt_version=_string_option(option_map, "--prompt-version", "prompt_v1"),
        seed=int(_required_option(option_map, "--seed")),
    )


def _string_option(
    option_map: dict[str, str | list[str]],
    option: str,
    default: str,
) -> str:
    value = option_map.get(option, default)
    if not isinstance(value, str):
        message = f"Unsupported duplicate option: {option}"
        raise _ExperimentCliUsageError(message)
    return value


def _parse_context_level(raw_value: str) -> PersonaContextLevel:
    try:
        return PersonaContextLevel(raw_value)
    except ValueError as error:
        message = f"Unsupported persona context level: {raw_value}"
        raise _ExperimentCliUsageError(message) from error
