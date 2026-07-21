"""Typed experiment-domain records for backend-first experiment storage."""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from synthetic_citizen_lab.experiments.context_models import (
    PersonaContextLevel,
    PersonaId,
)
from synthetic_citizen_lab.experiments.model_types import (
    CohortId,
    ComparisonId,
    FollowUpId,
    ProjectId,
    QuestionId,
    QuestionRelation,
    QuestionSetId,
    QuestionType,
    ResponseId,
    ResponseStatus,
    ReviewStatus,
    RunId,
    ScenarioId,
    ScenarioVariantLabel,
    StanceLabel,
)


class ScenarioVariantRecord(BaseModel):
    """One named scenario explanation variant."""

    model_config = ConfigDict(frozen=True)

    variant_id: ScenarioId
    label: ScenarioVariantLabel
    text: Annotated[str, StringConstraints(min_length=1)]


class ScenarioRecord(BaseModel):
    """Stored scenario definition with A/B/C-like variants."""

    model_config = ConfigDict(frozen=True)

    project_id: ProjectId
    scenario_id: ScenarioId
    title: Annotated[str, StringConstraints(min_length=1)]
    variants: tuple[ScenarioVariantRecord, ...] = Field(min_length=1)
    created_at: datetime

    @model_validator(mode="after")
    def _validate_unique_variant_labels(self) -> "ScenarioRecord":
        labels = tuple(variant.label for variant in self.variants)
        if len(labels) != len(set(labels)):
            message = "duplicate scenario variant labels are not allowed"
            raise ValueError(message)
        return self


class QuestionRecord(BaseModel):
    """One stored experiment question definition."""

    model_config = ConfigDict(frozen=True)

    question_id: QuestionId
    question_text: Annotated[str, StringConstraints(min_length=1)]
    question_type: QuestionType
    repeat_of_question_id: QuestionId | None = None

    @model_validator(mode="after")
    def _validate_repeat_link(self) -> "QuestionRecord":
        if self.question_type is QuestionType.SAME_QUESTION_REPEAT:
            if self.repeat_of_question_id is None:
                message = "repeat_of_question_id is required for SAME_QUESTION_REPEAT"
                raise ValueError(message)
        elif self.repeat_of_question_id is not None:
            message = (
                "repeat_of_question_id is only allowed for SAME_QUESTION_REPEAT"
            )
            raise ValueError(message)
        return self


class QuestionSetRecord(BaseModel):
    """Stored question-set definition for one experiment project."""

    model_config = ConfigDict(frozen=True)

    project_id: ProjectId
    question_set_id: QuestionSetId
    name: Annotated[str, StringConstraints(min_length=1)]
    questions: tuple[QuestionRecord, ...] = Field(min_length=1)
    created_at: datetime

    @model_validator(mode="after")
    def _validate_questions(self) -> "QuestionSetRecord":
        question_ids = tuple(question.question_id for question in self.questions)
        if len(question_ids) != len(set(question_ids)):
            message = "duplicate question_id values are not allowed"
            raise ValueError(message)
        indexed_questions = {
            question.question_id: question for question in self.questions
        }
        for question in self.questions:
            if question.repeat_of_question_id is None:
                continue
            referenced_question = indexed_questions.get(question.repeat_of_question_id)
            if referenced_question is None:
                message = (
                    "repeat_of_question_id must reference a question in the same "
                    "question set"
                )
                raise ValueError(message)
            if referenced_question.question_type is not QuestionType.ORIGINAL:
                message = "repeat_of_question_id must reference an ORIGINAL question"
                raise ValueError(message)
        return self


class GenerationConfig(BaseModel):
    """Stored generation settings for one run or response."""

    model_config = ConfigDict(frozen=True)

    model: Annotated[str, StringConstraints(min_length=1)]
    temperature: float = Field(ge=0.0, le=2.0)
    prompt_version: Annotated[str, StringConstraints(min_length=1)]


class RunRecord(BaseModel):
    """Stored experiment run metadata."""

    model_config = ConfigDict(frozen=True)

    project_id: ProjectId
    run_id: RunId
    cohort_id: CohortId
    scenario_id: ScenarioId
    question_set_id: QuestionSetId
    persona_context_level: PersonaContextLevel
    generation_config: GenerationConfig
    seed: int
    repeat_count: int = Field(ge=1)
    created_at: datetime


class StructuredResponse(BaseModel):
    """Minimal structured synthetic response payload."""

    model_config = ConfigDict(frozen=True)

    stance: StanceLabel
    stance_score: int = Field(ge=1, le=5)
    reasoning_summary: Annotated[str, StringConstraints(min_length=1)]
    concerns: tuple[str, ...] = Field(default_factory=tuple)
    acceptance_conditions: tuple[str, ...] = Field(default_factory=tuple)


class ResponseRecord(BaseModel):
    """Stored response row for one run/question/persona combination."""

    model_config = ConfigDict(frozen=True)

    project_id: ProjectId
    cohort_id: CohortId
    agent_id: PersonaId
    scenario_id: ScenarioId
    question_id: QuestionId
    run_id: RunId
    response_id: ResponseId
    repeat_index: int = Field(ge=0)
    question_type: QuestionType
    response_text: str | None
    structured_response: StructuredResponse | None
    generation_config: GenerationConfig
    status: ResponseStatus
    error_type: str | None
    created_at: datetime

    @model_validator(mode="after")
    def _validate_status_payload(self) -> "ResponseRecord":
        if self.status is ResponseStatus.SUCCESS:
            if self.response_text is None or self.structured_response is None:
                message = (
                    "success responses require response_text and "
                    "structured_response"
                )
                raise ValueError(message)
            if self.error_type is not None:
                message = "success responses must not include error_type"
                raise ValueError(message)
        elif self.error_type is None:
            message = "error responses require error_type"
            raise ValueError(message)
        return self


class AutomaticEvaluationRecord(BaseModel):
    """Stored automatic repeat-comparison summary."""

    model_config = ConfigDict(frozen=True)

    stance_match: bool
    stance_score_delta: int | None = None
    contradiction_candidate: bool
    needs_human_review: bool


class HumanEvaluationRecord(BaseModel):
    """Stored human-review summary for one comparison."""

    model_config = ConfigDict(frozen=True)

    review_status: ReviewStatus
    stance_consistency: str | None = None
    contradiction: str | None = None
    justified_change: str | None = None
    reviewer_confidence: str | None = None


class ComparisonRecord(BaseModel):
    """Stored comparison between two related responses."""

    model_config = ConfigDict(frozen=True)

    comparison_id: ComparisonId
    project_id: ProjectId
    run_id: RunId
    agent_id: PersonaId
    response_a_id: ResponseId
    response_b_id: ResponseId
    question_relation: QuestionRelation
    automatic_evaluation: AutomaticEvaluationRecord
    human_evaluation: HumanEvaluationRecord
    created_at: datetime

    @model_validator(mode="after")
    def _validate_response_pair(self) -> "ComparisonRecord":
        if self.response_a_id == self.response_b_id:
            message = "response_a_id and response_b_id must differ"
            raise ValueError(message)
        return self


class FollowUpRecord(BaseModel):
    """Stored limited follow-up linkage for one persona response."""

    model_config = ConfigDict(frozen=True)

    follow_up_id: FollowUpId
    project_id: ProjectId
    run_id: RunId
    parent_response_id: ResponseId
    agent_id: PersonaId
    question_id: QuestionId
    question_text: Annotated[str, StringConstraints(min_length=1)]
    response_id: ResponseId
    created_at: datetime


class ProjectRecord(BaseModel):
    """Stored project-level experiment metadata."""

    model_config = ConfigDict(frozen=True)

    project_id: ProjectId
    name: Annotated[str, StringConstraints(min_length=1)]
    research_goal: Annotated[str, StringConstraints(min_length=1)]
    non_claim: Annotated[str, StringConstraints(min_length=1)]
    created_at: datetime
