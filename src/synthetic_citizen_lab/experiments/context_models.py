"""Typed persona-context models and errors for experiment setup."""

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Final, NewType

from pydantic import BaseModel, ConfigDict

PersonaId = NewType("PersonaId", str)

P1_SOURCE_COLUMNS: Final[tuple[str, ...]] = (
    "uuid",
    "age",
    "sex",
    "region",
    "district",
    "marital_status",
    "education_level",
    "bachelors_field",
    "occupation",
    "family_type",
    "housing_type",
    "housing_tenure",
    "military_status",
    "economic_activity_status",
    "income_bracket",
)
HEALTH_SOURCE_COLUMNS: Final[tuple[str, ...]] = (
    "bmi_status",
    "blood_pressure_status",
    "blood_sugar_status",
    "waist_status",
    "smoking_status",
    "drinking_status",
)


class PersonaContextLevel(StrEnum):
    """Supported persona context detail levels."""

    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


@dataclass(frozen=True, slots=True)
class CohortArtifactNotFoundError(Exception):
    """Raised when a required cohort artifact is missing."""

    artifact_path: Path

    def __str__(self) -> str:
        """Return a readable cohort-artifact error."""
        return f"Missing cohort artifact: {self.artifact_path}"


@dataclass(frozen=True, slots=True)
class PersonaSourceNotFoundError(Exception):
    """Raised when the cohort points at a missing Parquet source."""

    source_path: Path

    def __str__(self) -> str:
        """Return a readable source-file error."""
        return f"Missing persona source Parquet: {self.source_path}"


@dataclass(frozen=True, slots=True)
class MissingPersonaColumnsError(Exception):
    """Raised when required persona-context columns are absent."""

    source_path: Path
    level: PersonaContextLevel
    columns: tuple[str, ...]

    def __str__(self) -> str:
        """Return a readable missing-columns error."""
        missing = ", ".join(self.columns)
        return (
            f"Source Parquet {self.source_path} is missing required {self.level} "
            f"columns: {missing}"
        )


@dataclass(frozen=True, slots=True)
class MissingSampledPersonasError(Exception):
    """Raised when sampled persona IDs are absent from the source."""

    source_path: Path
    persona_ids: tuple[PersonaId, ...]

    def __str__(self) -> str:
        """Return a readable sampled-persona error."""
        missing = ", ".join(self.persona_ids)
        return f"Missing sampled personas in {self.source_path}: {missing}"


class PersonaNarrative(BaseModel):
    """One retained narrative field for P3 context."""

    model_config = ConfigDict(frozen=True)

    field_name: str
    text: str


class PersonaContextP1(BaseModel):
    """Demographic and socioeconomic experiment context."""

    model_config = ConfigDict(frozen=True)

    persona_id: PersonaId
    age: int
    sex: str
    region: str
    district: str
    marital_status: str
    education_level: str
    bachelors_field: str
    occupation: str
    family_type: str
    housing_type: str
    housing_tenure: str
    military_status: str
    economic_activity_status: str
    income_bracket: str


class PersonaContextP2(PersonaContextP1):
    """P1 plus health and personality fields."""

    bmi_status: str
    blood_pressure_status: str
    blood_sugar_status: str
    waist_status: str
    smoking_status: str
    drinking_status: str
    openness: str
    conscientiousness: str
    extraversion: str
    agreeableness: str
    neuroticism: str


class PersonaContextP3(PersonaContextP2):
    """P2 plus narrative persona text."""

    narratives: tuple[PersonaNarrative, ...]


PersonaContext = PersonaContextP1 | PersonaContextP2 | PersonaContextP3
