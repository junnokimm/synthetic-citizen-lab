"""DuckDB-backed cohort counting and deterministic sampling."""

from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

import duckdb

from synthetic_citizen_lab.cohort.constants import PERSONA_ID_COLUMN, PREVIEW_COLUMNS
from synthetic_citizen_lab.cohort.fingerprint import sha256_file
from synthetic_citizen_lab.cohort.models import (
    BigFiveDiagnostics,
    CohortDefinition,
    CohortFilter,
    CohortRequest,
    SamplingSpec,
    SourceMetadata,
)
from synthetic_citizen_lab.cohort.query import (
    BIG_FIVE_SCORE_PATTERN,
    _quote_identifier,
    _sql_string,
    build_cohort_query,
    canonical_filter_payload,
    count_sql,
    select_sql,
)
from synthetic_citizen_lab.cohort.storage import (
    write_cohort_definition,
    write_preview,
    write_sample_ids,
)

PreviewValue = str | int | float | bool | None


class CohortSampler:
    """Count, sample, preview, and save cohorts from a source Parquet file."""

    def __init__(self, source_path: Path) -> None:
        """Create a sampler bound to one source Parquet file."""
        self._source_path = source_path.expanduser().resolve()

    def matching_count(self, filter_spec: CohortFilter) -> int:
        """Return the number of personas matching a cohort filter."""
        query = build_cohort_query(filter_spec)
        row = (
            _connect()
            .execute(count_sql(self._source_path, query), query.params)
            .fetchone()
        )
        return int(row[0])

    def sample_ids(
        self, filter_spec: CohortFilter, sampling: SamplingSpec
    ) -> tuple[str, ...]:
        """Return deterministic sampled uuid values for a cohort filter."""
        matching_count = self.matching_count(filter_spec)
        if matching_count == 0:
            message = "matching count is zero; cannot sample personas."
            raise ValueError(message)
        if sampling.sample_size > matching_count:
            message = "sample_size is larger than matching count."
            raise ValueError(message)
        query = build_cohort_query(filter_spec)
        sql = (
            select_sql(self._source_path, (PERSONA_ID_COLUMN,), query)
            + " GROUP BY uuid ORDER BY md5(uuid || '|' || ?) LIMIT ?"
        )
        params = (*query.params, str(sampling.seed), sampling.sample_size)
        rows = _connect().execute(sql, params).fetchall()
        return tuple(str(row[0]) for row in rows)

    def sample_preview(
        self, persona_ids: tuple[str, ...], limit: int = 20
    ) -> tuple[dict[str, PreviewValue], ...]:
        """Return safe preview rows for sampled uuid values."""
        if not persona_ids:
            return ()
        preview_ids = persona_ids[: max(limit, 0)]
        placeholders = "(" + ", ".join("?" for _ in preview_ids) + ")"
        order_case = " ".join(
            f"WHEN ? THEN {index}" for index, _ in enumerate(preview_ids)
        )
        sql = (
            select_sql(
                self._source_path, PREVIEW_COLUMNS, build_cohort_query(CohortFilter())
            )
            + f" AND uuid IN {placeholders} ORDER BY CASE uuid {order_case} END"
        )
        params = (*preview_ids, *preview_ids)
        rows = _connect().execute(sql, params).fetchall()
        return tuple(
            {
                column: _preview_value(value)
                for column, value in zip(PREVIEW_COLUMNS, row, strict=True)
            }
            for row in rows
        )

    def big_five_diagnostics(self, trait: str) -> BigFiveDiagnostics:
        """Return parse diagnostics for a Big Five JSON-string column."""
        if trait not in {
            "openness",
            "conscientiousness",
            "extraversion",
            "agreeableness",
            "neuroticism",
        }:
            message = f"Unsupported Big Five trait: {trait}"
            raise ValueError(message)
        trait_column = _quote_identifier(trait)
        sql = (
            f"SELECT COUNT(*), COUNT(TRY_CAST(regexp_extract({trait_column}, "
            f"'{BIG_FIVE_SCORE_PATTERN}', 1) AS INTEGER)) "
            f"FROM read_parquet({_sql_string(self._source_path)})"
        )
        row = _connect().execute(sql).fetchone()
        row_count = int(row[0])
        success = int(row[1])
        failures = row_count - success
        return BigFiveDiagnostics(
            trait=trait,
            row_count=row_count,
            parse_success_count=success,
            parse_failure_count=failures,
            parse_failure_ratio=failures / row_count,
        )

    def save_sample(self, request: CohortRequest, *, output_dir: Path) -> Path:
        """Write cohort metadata, sampled IDs, and a safe preview CSV."""
        persona_ids = self.sample_ids(request.filters, request.sampling)
        matching_count = self.matching_count(request.filters)
        source = SourceMetadata(
            path=self._source_path,
            sha256=sha256_file(self._source_path),
            row_count=self.matching_count(CohortFilter()),
        )
        query = build_cohort_query(request.filters)
        canonical = request.filters.canonical_json()
        filter_hash = sha256(canonical.encode("utf-8")).hexdigest()
        cohort_id = (
            "cohort_"
            + sha256(
                f"{source.sha256}|{canonical}|{request.sampling.model_dump_json()}".encode()
            ).hexdigest()[:16]
        )
        cohort_dir = output_dir / cohort_id
        definition = CohortDefinition(
            cohort_id=cohort_id,
            name=request.name,
            source=source,
            filters=canonical_filter_payload(request.filters),
            canonical_filter_json=canonical,
            filter_hash=filter_hash,
            human_readable_filter=query.summary,
            matching_count=matching_count,
            sampling=request.sampling,
            persona_ids=persona_ids,
            created_at=datetime.now(UTC),
        )
        write_cohort_definition(cohort_dir / "cohort.json", definition)
        write_sample_ids(cohort_dir / "sample_ids.csv", persona_ids)
        write_preview(
            cohort_dir / "sample_preview.csv", self.sample_preview(persona_ids)
        )
        return cohort_dir


def _connect() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(database=":memory:")


def _preview_value(value: PreviewValue) -> PreviewValue:
    return value
