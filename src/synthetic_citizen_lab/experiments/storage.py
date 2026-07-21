"""File-backed storage helpers for experiment-domain records."""

from pathlib import Path
from typing import Annotated, TypeVar

from pydantic import BaseModel, StringConstraints, TypeAdapter, ValidationError

from synthetic_citizen_lab.experiments.model_types import ProjectId, RunId
from synthetic_citizen_lab.experiments.models import (
    ComparisonRecord,
    FollowUpRecord,
    ProjectRecord,
    QuestionSetRecord,
    ResponseRecord,
    RunRecord,
    ScenarioRecord,
)

RecordT = TypeVar("RecordT", bound=BaseModel)
_PROJECT_ID_ADAPTER = TypeAdapter(ProjectId)
_RUN_ID_ADAPTER = TypeAdapter(RunId)
_COMPARISON_FILE_NAME_ADAPTER = TypeAdapter(
    Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*\.json$")]
)


def write_project_record(output_root: Path, record: ProjectRecord) -> Path:
    """Write one project record to its canonical JSON path."""
    path = _project_dir(output_root, record.project_id) / "project.json"
    return _write_json(path, record, output_root)


def write_scenario_record(output_root: Path, record: ScenarioRecord) -> Path:
    """Write one scenario record to its canonical JSON path."""
    path = (
        _project_dir(output_root, record.project_id)
        / "scenarios"
        / f"{record.scenario_id}.json"
    )
    return _write_json(path, record, output_root)


def write_question_set_record(output_root: Path, record: QuestionSetRecord) -> Path:
    """Write one question-set record to its canonical JSON path."""
    path = (
        _project_dir(output_root, record.project_id)
        / "question_sets"
        / f"{record.question_set_id}.json"
    )
    return _write_json(path, record, output_root)


def write_run_record(output_root: Path, record: RunRecord) -> Path:
    """Write one run record to its canonical JSON path."""
    path = _run_dir(output_root, record.project_id, record.run_id) / "run.json"
    return _write_json(path, record, output_root)


def write_response_records(
    output_root: Path,
    *,
    project_id: str,
    run_id: str,
    responses: tuple[ResponseRecord, ...],
) -> Path:
    """Write ordered response records to canonical JSONL storage."""
    validated_project_id = _validate_project_id(project_id)
    validated_run_id = _validate_run_id(run_id)
    _validate_response_scope(responses, validated_project_id, validated_run_id)
    path = (
        _run_dir(output_root, validated_project_id, validated_run_id)
        / "responses.jsonl"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = "\n".join(record.model_dump_json() for record in responses) + "\n"
    _assert_path_within_root(path, output_root)
    path.write_text(payload, encoding="utf-8")
    return path


def write_comparison_records(
    output_root: Path,
    *,
    project_id: str,
    run_id: str,
    file_name: str,
    comparisons: tuple[ComparisonRecord, ...],
) -> Path:
    """Write comparison records to one canonical JSON file."""
    validated_project_id = _validate_project_id(project_id)
    validated_run_id = _validate_run_id(run_id)
    validated_file_name = _validate_comparison_file_name(file_name)
    _validate_comparison_scope(comparisons, validated_project_id, validated_run_id)
    path = (
        _run_dir(output_root, validated_project_id, validated_run_id)
        / "comparisons"
        / validated_file_name
    )
    return _write_json(path, comparisons, output_root)


def write_follow_up_record(output_root: Path, record: FollowUpRecord) -> Path:
    """Write one follow-up record to its canonical JSON path."""
    path = (
        _run_dir(output_root, record.project_id, record.run_id)
        / "follow_ups"
        / f"{record.follow_up_id}.json"
    )
    return _write_json(path, record, output_root)


def load_project_record(path: Path) -> ProjectRecord:
    """Load one project record from JSON."""
    return ProjectRecord.model_validate_json(path.read_text(encoding="utf-8"))


def load_scenario_record(path: Path) -> ScenarioRecord:
    """Load one scenario record from JSON."""
    return ScenarioRecord.model_validate_json(path.read_text(encoding="utf-8"))


def load_question_set_record(path: Path) -> QuestionSetRecord:
    """Load one question-set record from JSON."""
    return QuestionSetRecord.model_validate_json(path.read_text(encoding="utf-8"))


def load_run_record(path: Path) -> RunRecord:
    """Load one run record from JSON."""
    return RunRecord.model_validate_json(path.read_text(encoding="utf-8"))


def load_response_records(path: Path) -> tuple[ResponseRecord, ...]:
    """Load ordered response records from JSONL."""
    lines = tuple(
        line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    )
    return tuple(ResponseRecord.model_validate_json(line) for line in lines)


def load_comparison_records(path: Path) -> tuple[ComparisonRecord, ...]:
    """Load comparison records from a JSON array file."""
    return TypeAdapter(tuple[ComparisonRecord, ...]).validate_json(
        path.read_text(encoding="utf-8")
    )


def load_follow_up_record(path: Path) -> FollowUpRecord:
    """Load one follow-up record from JSON."""
    return FollowUpRecord.model_validate_json(path.read_text(encoding="utf-8"))


def _write_json(
    path: Path,
    payload: BaseModel | tuple[ComparisonRecord, ...],
    output_root: Path,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    _assert_path_within_root(path, output_root)
    if isinstance(payload, BaseModel):
        path.write_text(payload.model_dump_json(indent=2), encoding="utf-8")
    else:
        serialized_payload = TypeAdapter(tuple[ComparisonRecord, ...]).dump_json(
            payload,
            indent=2,
        )
        path.write_text(serialized_payload.decode("utf-8"), encoding="utf-8")
    return path


def _project_dir(output_root: Path, project_id: str) -> Path:
    return output_root / project_id


def _run_dir(output_root: Path, project_id: str, run_id: str) -> Path:
    return _project_dir(output_root, project_id) / "runs" / run_id


def _validate_project_id(project_id: str) -> str:
    try:
        return _PROJECT_ID_ADAPTER.validate_python(project_id)
    except ValidationError as error:
        message = f"invalid project_id for storage path: {project_id}"
        raise ValueError(message) from error


def _validate_run_id(run_id: str) -> str:
    try:
        return _RUN_ID_ADAPTER.validate_python(run_id)
    except ValidationError as error:
        message = f"invalid run_id for storage path: {run_id}"
        raise ValueError(message) from error


def _validate_comparison_file_name(file_name: str) -> str:
    try:
        return _COMPARISON_FILE_NAME_ADAPTER.validate_python(file_name)
    except ValidationError as error:
        message = f"invalid file_name for comparison storage: {file_name}"
        raise ValueError(message) from error


def _validate_response_scope(
    responses: tuple[ResponseRecord, ...],
    project_id: str,
    run_id: str,
) -> None:
    for response in responses:
        if response.project_id != project_id:
            message = "response project_id does not match storage destination"
            raise ValueError(message)
        if response.run_id != run_id:
            message = "response run_id does not match storage destination"
            raise ValueError(message)


def _validate_comparison_scope(
    comparisons: tuple[ComparisonRecord, ...],
    project_id: str,
    run_id: str,
) -> None:
    for comparison in comparisons:
        if comparison.project_id != project_id:
            message = "comparison project_id does not match storage destination"
            raise ValueError(message)
        if comparison.run_id != run_id:
            message = "comparison run_id does not match storage destination"
            raise ValueError(message)


def _assert_path_within_root(path: Path, output_root: Path) -> None:
    resolved_root = output_root.expanduser().resolve()
    resolved_path = path.expanduser().resolve()
    if resolved_root not in resolved_path.parents and resolved_path != resolved_root:
        message = f"refusing to write outside output root: {resolved_path}"
        raise ValueError(message)
