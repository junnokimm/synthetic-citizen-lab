"""Typed category-profile result models."""

from pathlib import Path
from typing import TypeAlias

from pydantic import BaseModel, ConfigDict, Field

ProfileValue: TypeAlias = str | int | float | bool | None


class ValueFrequency(BaseModel):
    """Frequency summary for one categorical value."""

    model_config = ConfigDict(frozen=True)

    value: ProfileValue
    count: int
    ratio: float


class CategoricalColumnProfile(BaseModel):
    """Bounded value profile for one categorical column."""

    model_config = ConfigDict(frozen=True)

    column: str
    distinct_count: int
    values: tuple[ValueFrequency, ...]
    direct_ui_ready: bool
    normalization_note: str


class AgeProfile(BaseModel):
    """Numeric age statistics and decade distribution."""

    model_config = ConfigDict(frozen=True)
    minimum: int
    maximum: int
    mean: float
    median: float
    distribution: tuple[ValueFrequency, ...]


class BigFiveProfile(BaseModel):
    """Value-format profile for one Big Five column."""

    model_config = ConfigDict(frozen=True)
    column: str
    distinct_count: int
    examples: tuple[ProfileValue, ...]
    numeric_parseable: bool
    parseable_ratio: float


class NarrativeColumnProfile(BaseModel):
    """String-length and exact-duplicate profile for one narrative column."""

    model_config = ConfigDict(frozen=True)
    column: str
    min_length: int
    mean_length: float
    median_length: float
    p95_length: float
    max_length: int
    distinct_count: int
    duplicate_row_ratio: float
    top_exact_value_ratio: float


class CategoryProfileResult(BaseModel):
    """Complete Phase 2.5 profile artifact."""

    model_config = ConfigDict(frozen=True)
    source_path: Path
    row_count: int
    caveat: str
    categorical: dict[str, CategoricalColumnProfile] = Field(default_factory=dict)
    age: AgeProfile
    big_five: dict[str, BigFiveProfile] = Field(default_factory=dict)
    narrative: dict[str, NarrativeColumnProfile] = Field(default_factory=dict)
    income_bracket_order: tuple[ProfileValue, ...] = Field(default_factory=tuple)
    income_order_inferred: bool = False
    direct_ui_fields: tuple[str, ...] = Field(default_factory=tuple)
    normalization_needed: tuple[str, ...] = Field(default_factory=tuple)
    json_path: Path
    csv_path: Path
    markdown_path: Path
