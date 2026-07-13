"""Safe Parquet inspection without full-table materialization."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from hashlib import sha256
from pathlib import Path
from typing import Final

import duckdb
import pyarrow.parquet as pq

from synthetic_citizen_lab.data.heuristics import build_candidates, classify_column
from synthetic_citizen_lab.data.models import (
    ColumnInfo,
    FileInfo,
    InspectionResult,
    JsonValue,
    ParquetInfo,
)

MASKED_VALUE: Final[str] = "***MASKED***"
DEFAULT_SAMPLE_LIMIT: Final[int] = 5

SqlValue = str | int | float | bool | None | date | datetime | Decimal | bytes


@dataclass(frozen=True, slots=True)
class ColumnInspectionInput:
    """Source values needed to build one column inspection record."""

    name: str
    pyarrow_type: str
    duckdb_type: str
    null_count: int
    row_count: int


def inspect_parquet(
    parquet_path: Path,
    *,
    output_dir: Path,
    sample_limit: int = DEFAULT_SAMPLE_LIMIT,
) -> InspectionResult:
    """Inspect Parquet metadata and small previews using PyArrow and DuckDB."""
    source_path = parquet_path.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    parquet_file = pq.ParquetFile(source_path)
    metadata = parquet_file.metadata
    schema = parquet_file.schema_arrow
    duckdb_types = _duckdb_schema(source_path)
    null_counts = _null_counts(source_path, schema.names)
    columns = tuple(
        _column_info(
            ColumnInspectionInput(
                name=name,
                pyarrow_type=str(schema.field(name).type),
                duckdb_type=duckdb_types[name],
                null_count=null_counts[name],
                row_count=metadata.num_rows,
            )
        )
        for name in schema.names
    )
    candidates = build_candidates(columns)
    result = InspectionResult(
        file=FileInfo(
            path=source_path,
            exists=source_path.exists(),
            size_bytes=source_path.stat().st_size,
            sha256=_sha256_file(source_path),
        ),
        parquet=ParquetInfo(
            num_rows=metadata.num_rows,
            num_columns=metadata.num_columns,
            num_row_groups=metadata.num_row_groups,
        ),
        columns=columns,
        sample_rows=_sample_rows(source_path, columns, sample_limit),
        candidates=candidates,
        json_path=output_dir / "inspection.json",
        dictionary_path=output_dir / "data_dictionary.md",
    )
    _write_json(result)
    _write_dictionary(result.dictionary_path, result)
    return result


def write_dictionary(path: Path, result: InspectionResult) -> None:
    """Write a non-authoritative data dictionary draft for human review."""
    _write_dictionary(path, result)


def _column_info(column: ColumnInspectionInput) -> ColumnInfo:
    heuristic = classify_column(column.name)
    null_ratio = 0.0 if column.row_count == 0 else column.null_count / column.row_count
    return ColumnInfo(
        name=column.name,
        pyarrow_type=column.pyarrow_type,
        duckdb_type=column.duckdb_type,
        null_count=column.null_count,
        null_ratio=null_ratio,
        candidate_categories=heuristic.categories,
        privacy_risk=heuristic.privacy_risk,
    )


def _duckdb_schema(path: Path) -> dict[str, str]:
    sql = f"DESCRIBE SELECT * FROM read_parquet({_sql_string(path)})"
    rows = duckdb.connect(database=":memory:").execute(sql).fetchall()
    return {str(row[0]): str(row[1]) for row in rows}


def _null_counts(path: Path, columns: Sequence[str]) -> dict[str, int]:
    expressions = [
        (
            f"(COUNT(*) - COUNT({_quote_identifier(column)})) "
            f"AS {_quote_identifier(column)}"
        )
        for column in columns
    ]
    sql = f"SELECT {', '.join(expressions)} FROM read_parquet({_sql_string(path)})"
    row = duckdb.connect(database=":memory:").execute(sql).fetchone()
    return {column: int(row[index]) for index, column in enumerate(columns)}


def _sample_rows(
    path: Path,
    columns: Sequence[ColumnInfo],
    sample_limit: int,
) -> tuple[dict[str, JsonValue], ...]:
    names = tuple(column.name for column in columns)
    projection = ", ".join(_quote_identifier(name) for name in names)
    sql = (
        f"SELECT {projection} FROM read_parquet({_sql_string(path)}) "
        f"LIMIT {max(sample_limit, 0)}"
    )
    rows = duckdb.connect(database=":memory:").execute(sql).fetchall()
    privacy_columns = {column.name for column in columns if column.privacy_risk}
    return tuple(
        {
            name: (
                MASKED_VALUE
                if name in privacy_columns and value is not None
                else _json_value(value)
            )
            for name, value in zip(names, row, strict=True)
        }
        for row in rows
    )


def _json_value(value: SqlValue) -> JsonValue:
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, date):
        return value.isoformat()
    return value


def _write_json(result: InspectionResult) -> None:
    result.json_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")


def _write_dictionary(path: Path, result: InspectionResult) -> None:
    lines = [
        "# Data Dictionary Draft",
        "",
        "This file is an automatically generated draft for research-team review.",
        (
            "Column meanings are not confirmed. Unknown means the inspector could "
            "not infer semantics from the column name."
        ),
        "",
        f"Source: `{result.file.path}`",
        f"Rows: {result.parquet.num_rows}",
        f"Columns: {result.parquet.num_columns}",
        f"Row groups: {result.parquet.num_row_groups}",
        f"SHA-256: `{result.file.sha256}`",
        "",
        (
            "| Column | PyArrow type | DuckDB type | Null count | Null ratio | "
            "Candidate categories | Privacy risk | Semantic status |"
        ),
        "| --- | --- | --- | ---: | ---: | --- | --- | --- |",
    ]
    for column in result.columns:
        categories = ", ".join(column.candidate_categories) or "unknown"
        lines.append(
            f"| `{column.name}` | `{column.pyarrow_type}` | `{column.duckdb_type}` | "
            f"{column.null_count} | {column.null_ratio:.6f} | {categories} | "
            f"{column.privacy_risk} | {column.semantic_status} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _sha256_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sql_string(path: Path) -> str:
    return "'" + str(path).replace("'", "''") + "'"


def _quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'
