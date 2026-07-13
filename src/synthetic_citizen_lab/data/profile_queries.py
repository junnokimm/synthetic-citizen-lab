"""DuckDB aggregate queries for category profiling."""

from pathlib import Path

import duckdb

from synthetic_citizen_lab.data.profile_models import (
    AgeProfile,
    BigFiveProfile,
    CategoricalColumnProfile,
    NarrativeColumnProfile,
    ProfileValue,
    ValueFrequency,
)
from synthetic_citizen_lab.data.profile_targets import (
    BIG_FIVE_COLUMNS,
    CATEGORICAL_COLUMNS,
    DIRECT_UI_DISTINCT_LIMIT,
    NARRATIVE_COLUMNS,
)

SqlCell = str | int | float | bool | None


def available_columns(path: Path) -> frozenset[str]:
    """Return source Parquet column names without loading rows."""
    rows = (
        _connect()
        .execute(f"DESCRIBE SELECT * FROM read_parquet({_sql_string(path)})")
        .fetchall()
    )
    return frozenset(str(row[0]) for row in rows)


def row_count(path: Path) -> int:
    """Return total row count through DuckDB aggregation."""
    row = (
        _connect()
        .execute(f"SELECT COUNT(*) FROM read_parquet({_sql_string(path)})")
        .fetchone()
    )
    return int(row[0])


def categorical_profiles(
    path: Path,
    columns: frozenset[str],
    total_rows: int,
    top_n: int,
) -> dict[str, CategoricalColumnProfile]:
    """Profile configured categorical columns with bounded value frequencies."""
    profiles: dict[str, CategoricalColumnProfile] = {}
    for column in CATEGORICAL_COLUMNS:
        if column in columns:
            distinct_count = _distinct_count(path, column)
            profiles[column] = CategoricalColumnProfile(
                column=column,
                distinct_count=distinct_count,
                values=_value_frequencies(path, column, total_rows, top_n),
                direct_ui_ready=distinct_count <= DIRECT_UI_DISTINCT_LIMIT,
                normalization_note=_normalization_note(column, distinct_count),
            )
    return profiles


def age_profile(path: Path) -> AgeProfile:
    """Profile age statistics and decade buckets."""
    row = (
        _connect()
        .execute(
            f"""
        SELECT MIN(age), MAX(age), AVG(age), median(age)
        FROM read_parquet({_sql_string(path)})
        """
        )
        .fetchone()
    )
    buckets = (
        _connect()
        .execute(
            f"""
        SELECT CAST(FLOOR(age / 10) * 10 AS INTEGER) AS decade, COUNT(*) AS count
        FROM read_parquet({_sql_string(path)})
        GROUP BY decade
        ORDER BY decade
        """
        )
        .fetchall()
    )
    total = sum(int(bucket[1]) for bucket in buckets)
    return AgeProfile(
        minimum=int(row[0]),
        maximum=int(row[1]),
        mean=float(row[2]),
        median=float(row[3]),
        distribution=tuple(
            ValueFrequency(
                value=f"{int(bucket[0])}s",
                count=int(bucket[1]),
                ratio=int(bucket[1]) / total,
            )
            for bucket in buckets
        ),
    )


def big_five_profiles(
    path: Path,
    columns: frozenset[str],
) -> dict[str, BigFiveProfile]:
    """Profile Big Five value examples and numeric parseability."""
    return {
        column: _big_five_profile(path, column)
        for column in BIG_FIVE_COLUMNS
        if column in columns
    }


def narrative_profiles(
    path: Path,
    columns: frozenset[str],
    total_rows: int,
) -> dict[str, NarrativeColumnProfile]:
    """Profile narrative length statistics and exact duplicates."""
    return {
        column: _narrative_profile(path, column, total_rows)
        for column in NARRATIVE_COLUMNS
        if column in columns
    }


def _value_frequencies(
    path: Path,
    column: str,
    total_rows: int,
    top_n: int,
) -> tuple[ValueFrequency, ...]:
    quoted = _quote_identifier(column)
    sql = (
        f"SELECT {quoted} AS value, COUNT(*) AS count "
        f"FROM read_parquet({_sql_string(path)}) "
        f"GROUP BY {quoted} ORDER BY count DESC, value ASC LIMIT {max(top_n, 0)}"
    )
    rows = _connect().execute(sql).fetchall()
    return tuple(
        ValueFrequency(
            value=_profile_value(row[0]),
            count=int(row[1]),
            ratio=int(row[1]) / total_rows,
        )
        for row in rows
    )


def _big_five_profile(path: Path, column: str) -> BigFiveProfile:
    quoted = _quote_identifier(column)
    row = (
        _connect()
        .execute(
            f"""
        SELECT COUNT(DISTINCT {quoted}),
               COUNT(TRY_CAST({quoted} AS DOUBLE)),
               COUNT({quoted})
        FROM read_parquet({_sql_string(path)})
        """
        )
        .fetchone()
    )
    examples = (
        _connect()
        .execute(
            f"""
        SELECT {quoted}, COUNT(*) AS count
        FROM read_parquet({_sql_string(path)})
        GROUP BY {quoted}
        ORDER BY count DESC, {quoted} ASC
        LIMIT 10
        """
        )
        .fetchall()
    )
    parseable_count = int(row[1])
    non_null_count = int(row[2])
    parseable_ratio = 0.0 if non_null_count == 0 else parseable_count / non_null_count
    return BigFiveProfile(
        column=column,
        distinct_count=int(row[0]),
        examples=tuple(_profile_value(example[0]) for example in examples),
        numeric_parseable=parseable_ratio == 1.0,
        parseable_ratio=parseable_ratio,
    )


def _narrative_profile(
    path: Path,
    column: str,
    total_rows: int,
) -> NarrativeColumnProfile:
    quoted = _quote_identifier(column)
    row = (
        _connect()
        .execute(
            f"""
        SELECT MIN(LENGTH(CAST({quoted} AS VARCHAR))),
               AVG(LENGTH(CAST({quoted} AS VARCHAR))),
               median(LENGTH(CAST({quoted} AS VARCHAR))),
               quantile_cont(LENGTH(CAST({quoted} AS VARCHAR)), 0.95),
               MAX(LENGTH(CAST({quoted} AS VARCHAR))),
               COUNT(DISTINCT {quoted})
        FROM read_parquet({_sql_string(path)})
        """
        )
        .fetchone()
    )
    top_row = (
        _connect()
        .execute(
            f"""
        SELECT COUNT(*) AS count
        FROM read_parquet({_sql_string(path)})
        GROUP BY {quoted}
        ORDER BY count DESC
        LIMIT 1
        """
        )
        .fetchone()
    )
    distinct_count = int(row[5])
    return NarrativeColumnProfile(
        column=column,
        min_length=int(row[0]),
        mean_length=float(row[1]),
        median_length=float(row[2]),
        p95_length=float(row[3]),
        max_length=int(row[4]),
        distinct_count=distinct_count,
        duplicate_row_ratio=1 - (distinct_count / total_rows),
        top_exact_value_ratio=int(top_row[0]) / total_rows,
    )


def _distinct_count(path: Path, column: str) -> int:
    quoted = _quote_identifier(column)
    row = (
        _connect()
        .execute(
            f"SELECT COUNT(DISTINCT {quoted}) FROM read_parquet({_sql_string(path)})"
        )
        .fetchone()
    )
    return int(row[0])


def _normalization_note(column: str, distinct_count: int) -> str:
    if column == "income_bracket":
        return "Review value order before using as an ordered cohort filter."
    if distinct_count > DIRECT_UI_DISTINCT_LIMIT:
        return "Too many distinct values for direct select UI; normalize or search."
    return "Suitable for direct filter UI after research-team label review."


def _profile_value(value: SqlCell) -> ProfileValue:
    return value


def _connect() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(database=":memory:")


def _sql_string(path: Path) -> str:
    return "'" + str(path).replace("'", "''") + "'"


def _quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'
