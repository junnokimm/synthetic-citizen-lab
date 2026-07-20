"""Shared experiment-model scalar types and enums."""

from enum import StrEnum
from typing import Annotated

from pydantic import StringConstraints

ProjectId = Annotated[str, StringConstraints(pattern=r"^project_[a-z0-9._-]+$")]
CohortId = Annotated[str, StringConstraints(pattern=r"^cohort_[A-Za-z0-9._-]+$")]
ScenarioId = Annotated[str, StringConstraints(pattern=r"^scenario_[A-Za-z0-9._-]+$")]
QuestionSetId = Annotated[
    str, StringConstraints(pattern=r"^question_set_[A-Za-z0-9._-]+$")
]
QuestionId = Annotated[str, StringConstraints(pattern=r"^question_[A-Za-z0-9._-]+$")]
RunId = Annotated[str, StringConstraints(pattern=r"^run_[A-Za-z0-9._-]+$")]
ResponseId = Annotated[str, StringConstraints(pattern=r"^response_[A-Za-z0-9._-]+$")]
ComparisonId = Annotated[
    str, StringConstraints(pattern=r"^comparison_[A-Za-z0-9._-]+$")
]
FollowUpId = Annotated[str, StringConstraints(pattern=r"^follow_up_[A-Za-z0-9._-]+$")]


class ScenarioVariantLabel(StrEnum):
    """Supported scenario explanation labels."""

    A = "A"
    B = "B"
    C = "C"


class QuestionType(StrEnum):
    """Supported question types for this MVP."""

    ORIGINAL = "ORIGINAL"
    SAME_QUESTION_REPEAT = "SAME_QUESTION_REPEAT"
    FOLLOW_UP_LIMITED = "FOLLOW_UP_LIMITED"


class ResponseStatus(StrEnum):
    """Execution status for one generated response."""

    SUCCESS = "success"
    ERROR = "error"


class StanceLabel(StrEnum):
    """Minimal structured stance labels."""

    SUPPORT = "support"
    NEUTRAL = "neutral"
    OPPOSE = "oppose"


class QuestionRelation(StrEnum):
    """Supported comparison relations between stored responses."""

    SAME_QUESTION_REPEAT = "SAME_QUESTION_REPEAT"
    FOLLOW_UP_LIMITED = "FOLLOW_UP_LIMITED"


class ReviewStatus(StrEnum):
    """Human-review state for one comparison record."""

    NOT_REVIEWED = "not_reviewed"
    REVIEWED = "reviewed"
