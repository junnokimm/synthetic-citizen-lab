"""Internal parsing helpers for the experiment CLI."""

from dataclasses import dataclass
from pathlib import Path
from typing import Final

from synthetic_citizen_lab.experiments.model_types import (
    QuestionType,
    ScenarioVariantLabel,
)

DEFAULT_OUTPUT_DIR: Final[Path] = Path("outputs/experiments")
_VARIANT_PART_COUNT: Final[int] = 2
_QUESTION_PART_COUNTS: Final[frozenset[int]] = frozenset({3, 4})
_INIT_PROJECT_OPTIONS: Final[frozenset[str]] = frozenset(
    {"--output-dir", "--project-id", "--name", "--research-goal", "--non-claim"}
)
_SAVE_SCENARIO_OPTIONS: Final[frozenset[str]] = frozenset(
    {"--output-dir", "--project-id", "--scenario-id", "--title", "--variant"}
)
_SAVE_QUESTION_OPTIONS: Final[frozenset[str]] = frozenset(
    {"--output-dir", "--project-id", "--question-set-id", "--name", "--question"}
)
_SHOW_OPTIONS: Final[frozenset[str]] = frozenset(
    {"--output-dir", "--project-id", "--scenario-id", "--question-set-id"}
)


@dataclass(frozen=True, slots=True)
class _InitProjectArgs:
    output_dir: Path
    project_id: str
    name: str
    research_goal: str
    non_claim: str


@dataclass(frozen=True, slots=True)
class _ScenarioVariantInput:
    label: ScenarioVariantLabel
    text: str


@dataclass(frozen=True, slots=True)
class _SaveScenarioArgs:
    output_dir: Path
    project_id: str
    scenario_id: str
    title: str
    variants: tuple[_ScenarioVariantInput, ...]


@dataclass(frozen=True, slots=True)
class _QuestionInput:
    question_id: str
    question_type: QuestionType
    question_text: str
    repeat_of_question_id: str | None


@dataclass(frozen=True, slots=True)
class _SaveQuestionSetArgs:
    output_dir: Path
    project_id: str
    question_set_id: str
    name: str
    questions: tuple[_QuestionInput, ...]


@dataclass(frozen=True, slots=True)
class _ShowArgs:
    output_dir: Path
    resource_type: str
    project_id: str
    scenario_id: str | None
    question_set_id: str | None


class _ExperimentCliUsageError(Exception):
    pass


def _parse_init_project_args(argv: tuple[str, ...]) -> _InitProjectArgs:
    option_map = _parse_option_map(argv, allowed_options=_INIT_PROJECT_OPTIONS)
    return _InitProjectArgs(
        output_dir=Path(option_map.get("--output-dir", str(DEFAULT_OUTPUT_DIR))),
        project_id=_required_option(option_map, "--project-id"),
        name=_required_option(option_map, "--name"),
        research_goal=_required_option(option_map, "--research-goal"),
        non_claim=_required_option(option_map, "--non-claim"),
    )


def _parse_save_scenario_args(argv: tuple[str, ...]) -> _SaveScenarioArgs:
    option_map = _parse_option_map(
        argv,
        allowed_options=_SAVE_SCENARIO_OPTIONS,
        repeatable_options={"--variant"},
    )
    variant_values = option_map.get("--variant", [])
    if not variant_values:
        _raise_usage("save-scenario requires at least one --variant")
    if not isinstance(variant_values, list):
        _raise_usage("save-scenario received an invalid --variant payload")
    return _SaveScenarioArgs(
        output_dir=Path(option_map.get("--output-dir", str(DEFAULT_OUTPUT_DIR))),
        project_id=_required_option(option_map, "--project-id"),
        scenario_id=_required_option(option_map, "--scenario-id"),
        title=_required_option(option_map, "--title"),
        variants=tuple(_parse_variant(value) for value in variant_values),
    )


def _parse_save_question_set_args(argv: tuple[str, ...]) -> _SaveQuestionSetArgs:
    option_map = _parse_option_map(
        argv,
        allowed_options=_SAVE_QUESTION_OPTIONS,
        repeatable_options={"--question"},
    )
    question_values = option_map.get("--question", [])
    if not question_values:
        _raise_usage("save-questions requires at least one --question")
    if not isinstance(question_values, list):
        _raise_usage("save-questions received an invalid --question payload")
    return _SaveQuestionSetArgs(
        output_dir=Path(option_map.get("--output-dir", str(DEFAULT_OUTPUT_DIR))),
        project_id=_required_option(option_map, "--project-id"),
        question_set_id=_required_option(option_map, "--question-set-id"),
        name=_required_option(option_map, "--name"),
        questions=tuple(_parse_question(value) for value in question_values),
    )


def _parse_show_args(argv: tuple[str, ...]) -> _ShowArgs:
    if not argv:
        _raise_usage("show requires a resource type")
    resource_type = argv[0]
    option_map = _parse_option_map(argv[1:], allowed_options=_SHOW_OPTIONS)
    return _ShowArgs(
        output_dir=Path(option_map.get("--output-dir", str(DEFAULT_OUTPUT_DIR))),
        resource_type=resource_type,
        project_id=_required_option(option_map, "--project-id"),
        scenario_id=option_map.get("--scenario-id"),
        question_set_id=option_map.get("--question-set-id"),
    )


def _parse_option_map(
    argv: tuple[str, ...],
    *,
    allowed_options: frozenset[str],
    repeatable_options: set[str] | None = None,
) -> dict[str, str | list[str]]:
    allowed_repeatable = repeatable_options or set()
    option_map: dict[str, str | list[str]] = {}
    index = 0
    while index < len(argv):
        current_arg = argv[index]
        if not current_arg.startswith("--"):
            _raise_usage(f"Unsupported argument: {current_arg}")
        if current_arg not in allowed_options:
            _raise_usage(f"Unsupported option: {current_arg}")
        value = _next_value(argv, index, current_arg)
        if current_arg in allowed_repeatable:
            existing_values = option_map.setdefault(current_arg, [])
            if not isinstance(existing_values, list):
                _raise_usage(f"Unsupported duplicate option: {current_arg}")
            existing_values.append(value)
        else:
            if current_arg in option_map:
                _raise_usage(f"Unsupported duplicate option: {current_arg}")
            option_map[current_arg] = value
        index += 2
    return option_map


def _parse_variant(raw_variant: str) -> _ScenarioVariantInput:
    parts = raw_variant.split("|", maxsplit=1)
    if len(parts) != _VARIANT_PART_COUNT:
        _raise_usage("Scenario variants must use LABEL|TEXT")
    raw_label, text = parts
    try:
        label = ScenarioVariantLabel(raw_label)
    except ValueError as error:
        message = f"Unsupported scenario variant label: {raw_label}"
        raise _ExperimentCliUsageError(message) from error
    return _ScenarioVariantInput(label=label, text=text)


def _parse_question(raw_question: str) -> _QuestionInput:
    parts = raw_question.split("|")
    if len(parts) not in _QUESTION_PART_COUNTS:
        _raise_usage(
            "Questions must use question_id|QUESTION_TYPE|QUESTION_TEXT"
            "|repeat_of_question_id"
        )
    question_id, raw_type, question_text, *repeat_parts = parts
    try:
        question_type = QuestionType(raw_type)
    except ValueError as error:
        message = f"Unsupported question type: {raw_type}"
        raise _ExperimentCliUsageError(message) from error
    if question_type is QuestionType.FOLLOW_UP_LIMITED:
        _raise_usage("Unsupported question type: FOLLOW_UP_LIMITED")
    repeat_of_question_id = repeat_parts[0] if repeat_parts else None
    return _QuestionInput(
        question_id=question_id,
        question_type=question_type,
        question_text=question_text,
        repeat_of_question_id=repeat_of_question_id,
    )


def _required_option(option_map: dict[str, str | list[str]], option: str) -> str:
    value = option_map.get(option)
    if not isinstance(value, str):
        _raise_usage(f"Missing value for {option}")
    return value


def _next_value(argv: tuple[str, ...], index: int, option: str) -> str:
    value_index = index + 1
    if value_index >= len(argv):
        _raise_usage(f"Missing value for {option}")
    return argv[value_index]


def _raise_usage(message: str) -> None:
    raise _ExperimentCliUsageError(message)
