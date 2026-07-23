"""Internal command handlers for the experiment CLI."""

import sys
from datetime import UTC, datetime
from pathlib import Path

from pydantic import TypeAdapter, ValidationError

from synthetic_citizen_lab._experiment_cli_args import (
    _ExperimentCliUsageError,
    _InitProjectArgs,
    _raise_usage,
    _SaveQuestionSetArgs,
    _SaveScenarioArgs,
    _ShowArgs,
)
from synthetic_citizen_lab._experiment_cli_run_args import _RunArgs
from synthetic_citizen_lab.experiments.engines import MockResponseEngine
from synthetic_citizen_lab.experiments.model_types import (
    ProjectId,
    QuestionSetId,
    ScenarioId,
)
from synthetic_citizen_lab.experiments.models import (
    GenerationConfig,
    ProjectRecord,
    QuestionRecord,
    QuestionSetRecord,
    ScenarioRecord,
    ScenarioVariantRecord,
)
from synthetic_citizen_lab.experiments.runner import (
    RunExperimentRequest,
    run_experiment,
)
from synthetic_citizen_lab.experiments.storage import (
    load_project_record,
    load_question_set_record,
    load_scenario_record,
    write_project_record,
    write_question_set_record,
    write_scenario_record,
)

_PROJECT_ID_ADAPTER = TypeAdapter(ProjectId)
_SCENARIO_ID_ADAPTER = TypeAdapter(ScenarioId)
_QUESTION_SET_ID_ADAPTER = TypeAdapter(QuestionSetId)


def _handle_init_project(parsed: _InitProjectArgs) -> None:
    record = ProjectRecord(
        project_id=parsed.project_id,
        name=parsed.name,
        research_goal=parsed.research_goal,
        non_claim=parsed.non_claim,
        created_at=datetime.now(UTC),
    )
    project_path = write_project_record(parsed.output_dir, record)
    sys.stdout.write(f"project_path={project_path}\n")


def _handle_save_scenario(parsed: _SaveScenarioArgs) -> None:
    _require_project(parsed.output_dir, parsed.project_id)
    record = ScenarioRecord(
        project_id=parsed.project_id,
        scenario_id=parsed.scenario_id,
        title=parsed.title,
        variants=tuple(
            ScenarioVariantRecord(
                variant_id=f"{parsed.scenario_id}_{variant.label.lower()}",
                label=variant.label,
                text=variant.text,
            )
            for variant in parsed.variants
        ),
        created_at=datetime.now(UTC),
    )
    scenario_path = write_scenario_record(parsed.output_dir, record)
    sys.stdout.write(f"scenario_path={scenario_path}\n")


def _handle_save_questions(parsed: _SaveQuestionSetArgs) -> None:
    _require_project(parsed.output_dir, parsed.project_id)
    record = QuestionSetRecord(
        project_id=parsed.project_id,
        question_set_id=parsed.question_set_id,
        name=parsed.name,
        questions=tuple(
            QuestionRecord(
                question_id=question.question_id,
                question_text=question.question_text,
                question_type=question.question_type,
                repeat_of_question_id=question.repeat_of_question_id,
            )
            for question in parsed.questions
        ),
        created_at=datetime.now(UTC),
    )
    question_set_path = write_question_set_record(parsed.output_dir, record)
    sys.stdout.write(f"question_set_path={question_set_path}\n")


def _handle_show(parsed: _ShowArgs) -> None:
    project_dir = _project_dir(parsed.output_dir, parsed.project_id)
    match parsed.resource_type:
        case "project":
            record = load_project_record(project_dir / "project.json")
        case "scenario":
            if parsed.scenario_id is None:
                _raise_usage("show scenario requires --scenario-id")
            scenario_id = _validate_scenario_id(parsed.scenario_id)
            record = load_scenario_record(
                _safe_read_path(
                    parsed.output_dir,
                    project_dir / "scenarios" / f"{scenario_id}.json",
                )
            )
        case "question-set":
            if parsed.question_set_id is None:
                _raise_usage("show question-set requires --question-set-id")
            question_set_id = _validate_question_set_id(parsed.question_set_id)
            record = load_question_set_record(
                _safe_read_path(
                    parsed.output_dir,
                    project_dir / "question_sets" / f"{question_set_id}.json",
                )
            )
        case _:
            _raise_usage(f"Unsupported show resource: {parsed.resource_type}")
    sys.stdout.write(record.model_dump_json(indent=2) + "\n")


def _handle_run(parsed: _RunArgs) -> None:
    artifacts = run_experiment(
        RunExperimentRequest(
            output_root=parsed.output_dir,
            cohort_dir=parsed.cohort_dir,
            project_id=parsed.project_id,
            run_id=parsed.run_id,
            scenario_id=parsed.scenario_id,
            question_set_id=parsed.question_set_id,
            persona_context_level=parsed.persona_context_level,
            generation_config=GenerationConfig(
                model=parsed.model,
                temperature=parsed.temperature,
                prompt_version=parsed.prompt_version,
            ),
            seed=parsed.seed,
        ),
        response_engine=MockResponseEngine(),
    )
    sys.stdout.write(f"run_path={artifacts.run_path}\n")
    sys.stdout.write(f"responses_path={artifacts.responses_path}\n")


def _require_project(output_dir: Path, project_id: str) -> None:
    project_path = _project_dir(output_dir, project_id) / "project.json"
    if not project_path.exists():
        message = f"Project artifact not found: {project_path}"
        raise _ExperimentCliUsageError(message)


def _project_dir(output_dir: Path, project_id: str) -> Path:
    validated_project_id = _validate_project_id(project_id)
    return _safe_read_path(output_dir, output_dir / validated_project_id)


def _validate_project_id(project_id: str) -> str:
    return _validate_identifier(_PROJECT_ID_ADAPTER, project_id, "project_id")


def _validate_scenario_id(scenario_id: str) -> str:
    return _validate_identifier(_SCENARIO_ID_ADAPTER, scenario_id, "scenario_id")


def _validate_question_set_id(question_set_id: str) -> str:
    return _validate_identifier(
        _QUESTION_SET_ID_ADAPTER,
        question_set_id,
        "question_set_id",
    )


def _validate_identifier(
    adapter: TypeAdapter[str],
    raw_value: str,
    field_name: str,
) -> str:
    try:
        return adapter.validate_python(raw_value)
    except ValidationError as error:
        message = f"invalid {field_name}: {raw_value}"
        raise _ExperimentCliUsageError(message) from error


def _safe_read_path(output_dir: Path, path: Path) -> Path:
    resolved_root = output_dir.expanduser().resolve()
    resolved_path = path.expanduser().resolve()
    if resolved_path != resolved_root and resolved_root not in resolved_path.parents:
        message = f"refusing to read outside output root: {resolved_path}"
        raise _ExperimentCliUsageError(message)
    return resolved_path
