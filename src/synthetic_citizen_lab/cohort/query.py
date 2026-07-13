"""Safe DuckDB query construction for cohort filters."""

from dataclasses import dataclass
from pathlib import Path
from typing import Final

from synthetic_citizen_lab.cohort.constants import FILTER_FIELD_TO_COLUMN
from synthetic_citizen_lab.cohort.models import BigFiveFilter, CohortFilter

SqlParam = str | int | float

BIG_FIVE_SCORE_PATTERN: Final[str] = '"t_score"\\s*:\\s*([0-9]+)'
BIG_FIVE_LABEL_PATTERN: Final[str] = '"label"\\s*:\\s*"([^"\\n]+)"'


@dataclass(frozen=True, slots=True)
class CohortQuery:
    """SQL text, parameters, and readable summary for a cohort filter."""

    where_sql: str
    params: tuple[SqlParam, ...]
    summary: str


def build_cohort_query(filter_spec: CohortFilter) -> CohortQuery:
    """Build whitelisted SQL conditions and parameters for a cohort filter."""
    conditions: list[str] = []
    params: list[SqlParam] = []
    summaries: list[str] = []
    _add_age_conditions(filter_spec, conditions, params, summaries)
    for field_name, column in FILTER_FIELD_TO_COLUMN.items():
        values = getattr(filter_spec, field_name)
        if values:
            conditions.append(_in_condition(column, len(values)))
            params.extend(values)
            summaries.append(f"{column} in ({', '.join(values)})")
    if filter_spec.occupation_search:
        conditions.append("occupation LIKE ? ESCAPE '\\'")
        params.append(f"%{_escape_like(filter_spec.occupation_search)}%")
        summaries.append(f"occupation contains {filter_spec.occupation_search}")
    for trait, trait_filter in filter_spec.big_five_filters.items():
        _add_big_five_conditions(trait, trait_filter, conditions, params, summaries)
    where_sql = " AND ".join(conditions) if conditions else "TRUE"
    summary = "; ".join(summaries) if summaries else "all synthetic personas"
    return CohortQuery(where_sql=where_sql, params=tuple(params), summary=summary)


def select_sql(path: Path, projection: tuple[str, ...], query: CohortQuery) -> str:
    """Build a projected SELECT over a source Parquet path."""
    columns = ", ".join(_quote_identifier(column) for column in projection)
    return (
        f"SELECT {columns} FROM read_parquet({_sql_string(path)}) "
        f"WHERE {query.where_sql}"
    )


def count_sql(path: Path, query: CohortQuery) -> str:
    """Build a count query over a source Parquet path."""
    return (
        f"SELECT COUNT(*) FROM read_parquet({_sql_string(path)}) "
        f"WHERE {query.where_sql}"
    )


def canonical_filter_payload(filter_spec: CohortFilter) -> dict[str, str]:
    """Return a compact metadata representation of non-empty filters."""
    payload = filter_spec.model_dump(mode="json", exclude_none=True)
    return {str(key): str(value) for key, value in payload.items()}


def _add_age_conditions(
    filter_spec: CohortFilter,
    conditions: list[str],
    params: list[SqlParam],
    summaries: list[str],
) -> None:
    if filter_spec.age_min is not None:
        conditions.append("age >= ?")
        params.append(filter_spec.age_min)
        summaries.append(f"age >= {filter_spec.age_min}")
    if filter_spec.age_max is not None:
        conditions.append("age <= ?")
        params.append(filter_spec.age_max)
        summaries.append(f"age <= {filter_spec.age_max}")


def _add_big_five_conditions(
    trait: str,
    trait_filter: BigFiveFilter,
    conditions: list[str],
    params: list[SqlParam],
    summaries: list[str],
) -> None:
    score_expr = _big_five_score_expr(trait)
    label_expr = _big_five_label_expr(trait)
    if trait_filter.t_score_min is not None:
        conditions.append(f"{score_expr} >= ?")
        params.append(trait_filter.t_score_min)
        summaries.append(f"{trait}.t_score >= {trait_filter.t_score_min}")
    if trait_filter.t_score_max is not None:
        conditions.append(f"{score_expr} <= ?")
        params.append(trait_filter.t_score_max)
        summaries.append(f"{trait}.t_score <= {trait_filter.t_score_max}")
    if trait_filter.labels:
        conditions.append(f"{label_expr} IN {_placeholders(len(trait_filter.labels))}")
        params.extend(trait_filter.labels)
        summaries.append(f"{trait}.label in ({', '.join(trait_filter.labels)})")


def _big_five_score_expr(trait: str) -> str:
    return (
        f"TRY_CAST(regexp_extract({_quote_identifier(trait)}, "
        f"'{BIG_FIVE_SCORE_PATTERN}', 1) AS INTEGER)"
    )


def _big_five_label_expr(trait: str) -> str:
    return f"regexp_extract({_quote_identifier(trait)}, '{BIG_FIVE_LABEL_PATTERN}', 1)"


def _in_condition(column: str, count: int) -> str:
    return f"{_quote_identifier(column)} IN {_placeholders(count)}"


def _placeholders(count: int) -> str:
    return "(" + ", ".join("?" for _ in range(count)) + ")"


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _sql_string(path: Path) -> str:
    return "'" + str(path.expanduser().resolve()).replace("'", "''") + "'"


def _quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'
