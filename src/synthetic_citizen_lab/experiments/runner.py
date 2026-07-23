"""Experiment runner for mock phase-four execution."""

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import assert_never

from synthetic_citizen_lab.cohort.storage import load_cohort_definition
from synthetic_citizen_lab.experiments.context import load_persona_contexts
from synthetic_citizen_lab.experiments.context_models import (
    PersonaContext,
    PersonaContextLevel,
)
from synthetic_citizen_lab.experiments.engines import (
    EngineRequest,
    ResponseEngine,
    ResponseGenerationError,
)
from synthetic_citizen_lab.experiments.model_types import QuestionType, ResponseStatus
from synthetic_citizen_lab.experiments.models import (
    GenerationConfig,
    QuestionRecord,
    ResponseRecord,
    RunRecord,
    ScenarioRecord,
)
from synthetic_citizen_lab.experiments.storage import (
    load_question_set_record,
    load_scenario_record,
    write_response_records,
    write_run_record,
)


@dataclass(frozen=True, slots=True)
class RunExperimentRequest:
    """Inputs required to execute one deterministic experiment run."""

    output_root: Path
    cohort_dir: Path
    project_id: str
    run_id: str
    scenario_id: str
    question_set_id: str
    persona_context_level: PersonaContextLevel
    generation_config: GenerationConfig
    seed: int


@dataclass(frozen=True, slots=True)
class RunArtifacts:
    """Paths written by one completed run."""

    run_path: Path
    responses_path: Path


@dataclass(frozen=True, slots=True)
class _ResponseBuildContext:
    run_record: RunRecord
    scenario_record: ScenarioRecord
    question: QuestionRecord
    persona_context: PersonaContext
    response_engine: ResponseEngine
    created_at: datetime


def run_experiment(
    request: RunExperimentRequest,
    *,
    response_engine: ResponseEngine,
    created_at: datetime | None = None,
) -> RunArtifacts:
    """Execute one mock experiment run and persist canonical artifacts."""
    timestamp = created_at or datetime.now(UTC)
    cohort_definition = load_cohort_definition(request.cohort_dir / "cohort.json")
    scenario_record = load_scenario_record(
        request.output_root
        / request.project_id
        / "scenarios"
        / f"{request.scenario_id}.json"
    )
    question_set_record = load_question_set_record(
        request.output_root
        / request.project_id
        / "question_sets"
        / f"{request.question_set_id}.json"
    )
    persona_contexts = load_persona_contexts(
        request.cohort_dir,
        request.persona_context_level,
    )
    run_record = RunRecord(
        project_id=request.project_id,
        run_id=request.run_id,
        cohort_id=cohort_definition.cohort_id,
        scenario_id=request.scenario_id,
        question_set_id=request.question_set_id,
        persona_context_level=request.persona_context_level,
        generation_config=request.generation_config,
        seed=request.seed,
        repeat_count=_repeat_count(question_set_record.questions),
        created_at=timestamp,
    )
    responses = tuple(
        _build_response_record(
            _ResponseBuildContext(
                run_record=run_record,
                scenario_record=scenario_record,
                question=question,
                persona_context=persona_context,
                response_engine=response_engine,
                created_at=timestamp,
            )
        )
        for persona_context in persona_contexts
        for question in question_set_record.questions
    )
    run_path = write_run_record(request.output_root, run_record)
    responses_path = write_response_records(
        request.output_root,
        project_id=request.project_id,
        run_id=request.run_id,
        responses=responses,
    )
    return RunArtifacts(run_path=run_path, responses_path=responses_path)


def _repeat_count(questions: tuple[QuestionRecord, ...]) -> int:
    if any(
        question.question_type is QuestionType.SAME_QUESTION_REPEAT
        for question in questions
    ):
        return 2
    return 1


def _build_response_record(context: _ResponseBuildContext) -> ResponseRecord:
    repeat_index = _repeat_index(context.question)
    response_id = _response_id(
        context.run_record.run_id,
        str(context.persona_context.persona_id),
        context.question.question_id,
        repeat_index,
    )
    try:
        generated_response = context.response_engine.generate_response(
            EngineRequest(
                persona_context=context.persona_context,
                scenario=context.scenario_record,
                question=context.question,
                run=context.run_record,
                repeat_index=repeat_index,
            )
        )
    except ResponseGenerationError as error:
        return ResponseRecord(
            project_id=context.run_record.project_id,
            cohort_id=context.run_record.cohort_id,
            agent_id=context.persona_context.persona_id,
            scenario_id=context.run_record.scenario_id,
            question_id=context.question.question_id,
            run_id=context.run_record.run_id,
            response_id=response_id,
            repeat_index=repeat_index,
            question_type=context.question.question_type,
            response_text=None,
            structured_response=None,
            generation_config=context.run_record.generation_config,
            status=ResponseStatus.ERROR,
            error_type=type(error).__name__,
            created_at=context.created_at,
        )
    return ResponseRecord(
        project_id=context.run_record.project_id,
        cohort_id=context.run_record.cohort_id,
        agent_id=context.persona_context.persona_id,
        scenario_id=context.run_record.scenario_id,
        question_id=context.question.question_id,
        run_id=context.run_record.run_id,
        response_id=response_id,
        repeat_index=repeat_index,
        question_type=context.question.question_type,
        response_text=generated_response.response_text,
        structured_response=generated_response.structured_response,
        generation_config=context.run_record.generation_config,
        status=ResponseStatus.SUCCESS,
        error_type=None,
        created_at=context.created_at,
    )


def _repeat_index(question: QuestionRecord) -> int:
    match question.question_type:
        case QuestionType.ORIGINAL:
            return 0
        case QuestionType.SAME_QUESTION_REPEAT:
            return 1
        case QuestionType.FOLLOW_UP_LIMITED:
            message = "FOLLOW_UP_LIMITED is not supported by the phase-4 runner"
            raise ValueError(message)
        case unreachable:
            assert_never(unreachable)


def _response_id(
    run_id: str,
    persona_id: str,
    question_id: str,
    repeat_index: int,
) -> str:
    digest = hashlib.sha256(
        f"{run_id}|{persona_id}|{question_id}|{repeat_index}".encode()
    ).hexdigest()[:12]
    return f"response_{digest}"
