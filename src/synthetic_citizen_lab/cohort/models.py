"""Typed cohort filter, sampling, and saved-definition models."""

import json
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationInfo,
    field_validator,
    model_validator,
)

from synthetic_citizen_lab.cohort.constants import (
    BIG_FIVE_TRAITS,
    CATEGORICAL_ALLOWED,
    INCOME_BRACKET_ORDER,
)

FilterScalar = str | int | float | bool | None
FilterNested = FilterScalar | list[FilterScalar]
FilterValue = FilterScalar | list[FilterScalar] | dict[str, FilterNested]


class BigFiveFilter(BaseModel):
    """Optional filters for one Big Five JSON-string column."""

    model_config = ConfigDict(frozen=True)
    t_score_min: int | None = None
    t_score_max: int | None = None
    labels: tuple[str, ...] = Field(default_factory=tuple)

    @model_validator(mode="after")
    def _check_t_score_range(self) -> "BigFiveFilter":
        if (
            self.t_score_min is not None
            and self.t_score_max is not None
            and self.t_score_min > self.t_score_max
        ):
            message = "Big Five t_score_min cannot be greater than t_score_max."
            raise ValueError(message)
        return self


class CohortFilter(BaseModel):
    """User-defined cohort filter over approved source columns."""

    model_config = ConfigDict(frozen=True)
    age_min: int | None = None
    age_max: int | None = None
    sexes: tuple[str, ...] = Field(default_factory=tuple)
    regions: tuple[str, ...] = Field(default_factory=tuple)
    districts: tuple[str, ...] = Field(default_factory=tuple)
    marital_statuses: tuple[str, ...] = Field(default_factory=tuple)
    education_levels: tuple[str, ...] = Field(default_factory=tuple)
    bachelors_fields: tuple[str, ...] = Field(default_factory=tuple)
    occupations: tuple[str, ...] = Field(default_factory=tuple)
    occupation_search: str | None = None
    family_types: tuple[str, ...] = Field(default_factory=tuple)
    housing_types: tuple[str, ...] = Field(default_factory=tuple)
    housing_tenures: tuple[str, ...] = Field(default_factory=tuple)
    military_statuses: tuple[str, ...] = Field(default_factory=tuple)
    economic_activity_statuses: tuple[str, ...] = Field(default_factory=tuple)
    income_brackets: tuple[str, ...] = Field(default_factory=tuple)
    bmi_statuses: tuple[str, ...] = Field(default_factory=tuple)
    blood_pressure_statuses: tuple[str, ...] = Field(default_factory=tuple)
    blood_sugar_statuses: tuple[str, ...] = Field(default_factory=tuple)
    waist_statuses: tuple[str, ...] = Field(default_factory=tuple)
    smoking_statuses: tuple[str, ...] = Field(default_factory=tuple)
    drinking_statuses: tuple[str, ...] = Field(default_factory=tuple)
    big_five_filters: dict[str, BigFiveFilter] = Field(default_factory=dict)

    @field_validator("sexes")
    @classmethod
    def _validate_sexes(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return _validate_known_values("sex", value)

    @field_validator("education_levels")
    @classmethod
    def _validate_education_levels(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return _validate_known_values("education_level", value)

    @field_validator("economic_activity_statuses")
    @classmethod
    def _validate_economic_activity(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return _validate_known_values("economic_activity_status", value)

    @field_validator("income_brackets")
    @classmethod
    def _validate_income_brackets(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return _validate_known_values("income_bracket", value)

    @field_validator(
        "bmi_statuses",
        "blood_pressure_statuses",
        "blood_sugar_statuses",
        "waist_statuses",
        "smoking_statuses",
        "drinking_statuses",
    )
    @classmethod
    def _validate_health_values(
        cls,
        value: tuple[str, ...],
        info: ValidationInfo,
    ) -> tuple[str, ...]:
        field_to_column = {
            "bmi_statuses": "bmi_status",
            "blood_pressure_statuses": "blood_pressure_status",
            "blood_sugar_statuses": "blood_sugar_status",
            "waist_statuses": "waist_status",
            "smoking_statuses": "smoking_status",
            "drinking_statuses": "drinking_status",
        }
        return _validate_known_values(field_to_column[info.field_name], value)

    @model_validator(mode="after")
    def _check_ranges_and_traits(self) -> "CohortFilter":
        if (
            self.age_min is not None
            and self.age_max is not None
            and self.age_min > self.age_max
        ):
            message = "age_min cannot be greater than age_max."
            raise ValueError(message)
        invalid_traits = set(self.big_five_filters) - set(BIG_FIVE_TRAITS)
        if invalid_traits:
            message = f"Unsupported Big Five trait: {', '.join(sorted(invalid_traits))}"
            raise ValueError(message)
        return self

    @staticmethod
    def income_bracket_index(value: str) -> int:
        """Return the configured ordinal index for an income-bracket label."""
        return INCOME_BRACKET_ORDER.index(value)

    def canonical_json(self) -> str:
        """Return deterministic JSON for cohort hashing and reproducibility."""
        return json.dumps(
            self.model_dump(mode="json", exclude_none=True),
            ensure_ascii=False,
            sort_keys=True,
        )


class SamplingSpec(BaseModel):
    """Deterministic sample specification."""

    model_config = ConfigDict(frozen=True)
    sample_size: int
    seed: int
    method: Literal["deterministic_random"] = "deterministic_random"

    @field_validator("sample_size")
    @classmethod
    def _validate_sample_size(cls, value: int) -> int:
        if value < 1:
            message = "sample_size must be at least 1."
            raise ValueError(message)
        return value


class CohortRequest(BaseModel):
    """Inputs required to save a sampled cohort."""

    model_config = ConfigDict(frozen=True)
    name: str
    filters: CohortFilter
    sampling: SamplingSpec


class SourceMetadata(BaseModel):
    """Source Parquet identity stored with cohort outputs."""

    model_config = ConfigDict(frozen=True)
    path: Path
    sha256: str
    row_count: int


class CohortDefinition(BaseModel):
    """Saved cohort metadata and sampled Persona IDs."""

    model_config = ConfigDict(frozen=True)
    cohort_id: str
    name: str
    source: SourceMetadata
    filters: dict[str, str]
    canonical_filter_json: str
    filter_hash: str
    human_readable_filter: str
    matching_count: int
    sampling: SamplingSpec
    persona_ids: tuple[str, ...]
    created_at: datetime


class BigFiveDiagnostics(BaseModel):
    """Parse diagnostics for one Big Five source column."""

    model_config = ConfigDict(frozen=True)
    trait: str
    row_count: int
    parse_success_count: int
    parse_failure_count: int
    parse_failure_ratio: float


def _validate_known_values(column: str, values: tuple[str, ...]) -> tuple[str, ...]:
    allowed = CATEGORICAL_ALLOWED[column]
    invalid = set(values) - set(allowed)
    if invalid:
        message = f"Unsupported {column} value: {', '.join(sorted(invalid))}"
        raise ValueError(message)
    return values
