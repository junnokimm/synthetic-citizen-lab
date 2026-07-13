"""Column heuristics for draft data dictionaries."""

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Final

from synthetic_citizen_lab.data.models import CandidateColumns, ColumnInfo

PERSONA_ID_PATTERNS: Final[tuple[str, ...]] = (
    "persona_id",
    "personaid",
    "person_id",
    "uuid",
    "식별자",
)
DEMOGRAPHIC_PATTERNS: Final[tuple[str, ...]] = (
    "age",
    "gender",
    "sex",
    "region",
    "birth",
    "연령",
    "나이",
    "성별",
    "지역",
    "거주",
)
SOCIOECONOMIC_PATTERNS: Final[tuple[str, ...]] = (
    "job",
    "occupation",
    "income",
    "education",
    "economic",
    "employment",
    "직업",
    "소득",
    "학력",
    "고용",
)
HEALTH_PATTERNS: Final[tuple[str, ...]] = (
    "health",
    "disease",
    "disability",
    "medical",
    "bmi",
    "blood",
    "waist",
    "smoking",
    "drinking",
    "건강",
    "질병",
    "장애",
    "의료",
)
BIG_FIVE_PATTERNS: Final[tuple[str, ...]] = (
    "openness",
    "conscientiousness",
    "extraversion",
    "agreeableness",
    "neuroticism",
    "big_five",
    "bigfive",
    "개방성",
    "성실성",
    "외향성",
    "우호성",
    "신경성",
)
NARRATIVE_PATTERNS: Final[tuple[str, ...]] = (
    "narrative",
    "story",
    "bio",
    "description",
    "profile",
    "persona",
    "서사",
    "스토리",
    "소개",
    "설명",
)
IDENTIFYING_PATTERNS: Final[tuple[str, ...]] = (
    "name",
    "address",
    "street",
    "postcode",
    "unit",
    "city",
    "phone",
    "mobile",
    "email",
    "contact",
    "resident",
    "이름",
    "성명",
    "주소",
    "상세주소",
    "전화",
    "휴대폰",
    "연락처",
    "이메일",
    "주민",
)


@dataclass(frozen=True, slots=True)
class ColumnHeuristic:
    """Heuristic categories for one source column."""

    categories: tuple[str, ...]
    privacy_risk: bool


def classify_column(name: str) -> ColumnHeuristic:
    """Classify a column name into non-authoritative candidate groups."""
    normalized = name.lower().replace(" ", "_")
    categories: list[str] = []
    if _is_persona_id_candidate(normalized):
        categories.append("persona_id")
    if _matches(normalized, DEMOGRAPHIC_PATTERNS):
        categories.append("demographic")
    if _matches(normalized, SOCIOECONOMIC_PATTERNS):
        categories.append("socioeconomic")
    if _matches(normalized, HEALTH_PATTERNS):
        categories.append("health")
    if _matches(normalized, BIG_FIVE_PATTERNS):
        categories.append("big_five")
    if _matches(normalized, NARRATIVE_PATTERNS):
        categories.append("narrative")
    privacy_risk = _matches(normalized, IDENTIFYING_PATTERNS)
    if privacy_risk:
        categories.append("sensitive_or_identifying")
    return ColumnHeuristic(categories=tuple(categories), privacy_risk=privacy_risk)


def build_candidates(columns: Iterable[ColumnInfo]) -> CandidateColumns:
    """Collect per-column heuristics into candidate groups."""
    persona_id: list[str] = []
    demographic: list[str] = []
    socioeconomic: list[str] = []
    health: list[str] = []
    big_five: list[str] = []
    narrative: list[str] = []
    sensitive: list[str] = []
    for column in columns:
        if "persona_id" in column.candidate_categories:
            persona_id.append(column.name)
        if "demographic" in column.candidate_categories:
            demographic.append(column.name)
        if "socioeconomic" in column.candidate_categories:
            socioeconomic.append(column.name)
        if "health" in column.candidate_categories:
            health.append(column.name)
        if "big_five" in column.candidate_categories:
            big_five.append(column.name)
        if "narrative" in column.candidate_categories:
            narrative.append(column.name)
        if column.privacy_risk:
            sensitive.append(column.name)
    return CandidateColumns(
        persona_id=tuple(persona_id),
        demographic=tuple(demographic),
        socioeconomic=tuple(socioeconomic),
        health=tuple(health),
        big_five=tuple(big_five),
        narrative=tuple(narrative),
        sensitive_or_identifying=tuple(sensitive),
    )


def _matches(name: str, patterns: tuple[str, ...]) -> bool:
    return any(pattern in name for pattern in patterns)


def _is_persona_id_candidate(name: str) -> bool:
    return name == "id" or name.endswith("_id") or _matches(name, PERSONA_ID_PATTERNS)
