"""Typed data-inspection result models."""

from pathlib import Path
from typing import TypeAlias

from pydantic import BaseModel, ConfigDict, Field

JsonValue: TypeAlias = str | int | float | bool | None


class FileInfo(BaseModel):
    """Filesystem metadata for the inspected source file."""

    model_config = ConfigDict(frozen=True)

    path: Path
    exists: bool
    size_bytes: int
    sha256: str


class ParquetInfo(BaseModel):
    """Parquet footer metadata that can be read without loading all rows."""

    model_config = ConfigDict(frozen=True)

    num_rows: int
    num_columns: int
    num_row_groups: int


class ColumnInfo(BaseModel):
    """Column-level schema and null-profile information."""

    model_config = ConfigDict(frozen=True)

    name: str
    pyarrow_type: str
    duckdb_type: str
    null_count: int
    null_ratio: float
    semantic_status: str = "unknown"
    candidate_categories: tuple[str, ...] = Field(default_factory=tuple)
    privacy_risk: bool = False


class CandidateColumns(BaseModel):
    """Heuristic column groups for research-team review."""

    model_config = ConfigDict(frozen=True)

    persona_id: tuple[str, ...] = Field(default_factory=tuple)
    demographic: tuple[str, ...] = Field(default_factory=tuple)
    socioeconomic: tuple[str, ...] = Field(default_factory=tuple)
    health: tuple[str, ...] = Field(default_factory=tuple)
    big_five: tuple[str, ...] = Field(default_factory=tuple)
    narrative: tuple[str, ...] = Field(default_factory=tuple)
    sensitive_or_identifying: tuple[str, ...] = Field(default_factory=tuple)


class InspectionResult(BaseModel):
    """Complete artifact produced by a Phase 2 data-inspection run."""

    model_config = ConfigDict(frozen=True)
    file: FileInfo
    parquet: ParquetInfo
    columns: tuple[ColumnInfo, ...]
    sample_rows: tuple[dict[str, JsonValue], ...]
    candidates: CandidateColumns
    json_path: Path
    dictionary_path: Path
