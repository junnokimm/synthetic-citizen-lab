"""Deterministic response-engine helpers for experiment execution."""

import hashlib
from dataclasses import dataclass
from typing import Final, Protocol, assert_never

from synthetic_citizen_lab.experiments.context_models import PersonaContext, PersonaId
from synthetic_citizen_lab.experiments.model_types import StanceLabel
from synthetic_citizen_lab.experiments.models import (
    QuestionRecord,
    RunRecord,
    ScenarioRecord,
    StructuredResponse,
)

_STANCE_LABELS: Final[tuple[StanceLabel, ...]] = (
    StanceLabel.SUPPORT,
    StanceLabel.NEUTRAL,
    StanceLabel.OPPOSE,
)
_CONCERN_POOL: Final[tuple[str, ...]] = (
    "비용 부담",
    "형평성",
    "실행 준비",
    "개인정보",
    "접근성",
)
_ACCEPTANCE_POOL: Final[tuple[str, ...]] = (
    "단계적 시행",
    "보조금",
    "명확한 안내",
    "시범 운영",
    "안전장치",
)


@dataclass(frozen=True, slots=True)
class EngineRequest:
    """All inputs required to generate one response."""

    persona_context: PersonaContext
    scenario: ScenarioRecord
    question: QuestionRecord
    run: RunRecord
    repeat_index: int


@dataclass(frozen=True, slots=True)
class GeneratedResponse:
    """Successful generated response payload."""

    response_text: str
    structured_response: StructuredResponse


@dataclass(frozen=True, slots=True)
class ResponseGenerationError(Exception):
    """Raised when a configured engine failure should become an error record."""

    persona_id: PersonaId

    def __str__(self) -> str:
        """Return a readable generation failure message."""
        return f"Mock response generation failed for {self.persona_id}"


class ResponseEngine(Protocol):
    """Interface for response engines used by the runner."""

    def generate_response(self, request: EngineRequest) -> GeneratedResponse:
        """Return one generated response for the supplied request."""
        ...


@dataclass(frozen=True, slots=True)
class MockResponseEngine:
    """Deterministic mock engine for phase-four execution."""

    failure_persona_ids: frozenset[PersonaId] = frozenset()

    def generate_response(self, request: EngineRequest) -> GeneratedResponse:
        """Return a stable mock response for one request."""
        if request.persona_context.persona_id in self.failure_persona_ids:
            raise ResponseGenerationError(request.persona_context.persona_id)

        digest = hashlib.sha256(_request_payload(request).encode("utf-8")).digest()
        stance = _STANCE_LABELS[digest[0] % len(_STANCE_LABELS)]
        stance_score = _stance_score(stance, digest[1])
        concerns = _pick_labels(_CONCERN_POOL, digest[2], digest[3])
        acceptance_conditions = _pick_labels(_ACCEPTANCE_POOL, digest[4], digest[5])
        reasoning_summary = (
            f"{request.persona_context.region} "
            f"{request.persona_context.occupation} 관점에서 "
            f"{request.question.question_type} 응답을 구성함"
        )
        response_text = (
            f"{_stance_text(stance)}. {request.persona_context.occupation}로서 "
            f"{', '.join(concerns)}을(를) 우려하며, "
            f"{', '.join(acceptance_conditions)}이 있으면 수용 가능합니다."
        )
        return GeneratedResponse(
            response_text=response_text,
            structured_response=StructuredResponse(
                stance=stance,
                stance_score=stance_score,
                reasoning_summary=reasoning_summary,
                concerns=concerns,
                acceptance_conditions=acceptance_conditions,
            ),
        )


def _request_payload(request: EngineRequest) -> str:
    variant_payload = "|".join(
        f"{variant.label}:{variant.text}" for variant in request.scenario.variants
    )
    return "||".join(
        (
            str(request.persona_context.persona_id),
            request.question.question_id,
            request.question.question_text,
            request.scenario.scenario_id,
            variant_payload,
            request.run.run_id,
            str(request.run.seed),
            str(request.repeat_index),
            request.persona_context.model_dump_json(),
        )
    )


def _stance_score(stance: StanceLabel, signal: int) -> int:
    match stance:
        case StanceLabel.SUPPORT:
            return 4 + (signal % 2)
        case StanceLabel.NEUTRAL:
            return 3
        case StanceLabel.OPPOSE:
            return 1 + (signal % 2)
        case unreachable:
            assert_never(unreachable)


def _pick_labels(pool: tuple[str, ...], first: int, second: int) -> tuple[str, ...]:
    first_label = pool[first % len(pool)]
    second_label = pool[second % len(pool)]
    if first_label == second_label:
        return (first_label,)
    return (first_label, second_label)


def _stance_text(stance: StanceLabel) -> str:
    match stance:
        case StanceLabel.SUPPORT:
            return "전반적으로 찬성합니다"
        case StanceLabel.NEUTRAL:
            return "유보적인 입장입니다"
        case StanceLabel.OPPOSE:
            return "현재 조건에서는 반대합니다"
        case unreachable:
            assert_never(unreachable)
