"""Option lookup helpers for future cohort filter UI."""

from pathlib import Path

import duckdb

from synthetic_citizen_lab.cohort.query import _quote_identifier, _sql_string


class CohortOptions:
    """Read-only option lookup over approved cohort source columns."""

    def __init__(self, source_path: Path) -> None:
        """Create an option lookup bound to one source Parquet file."""
        self._source_path = source_path.expanduser().resolve()

    def regions(self) -> tuple[str, ...]:
        """Return distinct region names."""
        return self.distinct_values("region")

    def districts(self, regions: tuple[str, ...] = ()) -> tuple[str, ...]:
        """Return distinct districts, optionally constrained by regions."""
        params: list[str] = []
        where_sql = "TRUE"
        if regions:
            where_sql = "region IN (" + ", ".join("?" for _ in regions) + ")"
            params.extend(regions)
        sql = (
            "SELECT DISTINCT district "
            f"FROM read_parquet({_sql_string(self._source_path)}) "
            f"WHERE {where_sql} ORDER BY district"
        )
        rows = duckdb.connect(database=":memory:").execute(sql, params).fetchall()
        return tuple(str(row[0]) for row in rows)

    def distinct_values(
        self, column: str, with_counts: bool = False
    ) -> tuple[str, ...]:
        """Return distinct values for an approved cohort option column."""
        quoted = _quote_identifier(column)
        count_expr = ", COUNT(*) AS count" if with_counts else ""
        order_expr = "count DESC, value ASC" if with_counts else "value ASC"
        sql = (
            f"SELECT {quoted} AS value{count_expr} "
            f"FROM read_parquet({_sql_string(self._source_path)}) "
            f"GROUP BY {quoted} ORDER BY {order_expr}"
        )
        rows = duckdb.connect(database=":memory:").execute(sql).fetchall()
        if with_counts:
            return tuple(f"{row[0]}\t{row[1]}" for row in rows)
        return tuple(str(row[0]) for row in rows)

    def occupation_search(self, search: str) -> tuple[str, ...]:
        """Return distinct occupations containing a literal search string."""
        pattern = "%" + search.replace("\\", "\\\\").replace("%", "\\%") + "%"
        sql = (
            "SELECT DISTINCT occupation "
            f"FROM read_parquet({_sql_string(self._source_path)}) "
            "WHERE occupation LIKE ? ESCAPE '\\' ORDER BY occupation"
        )
        rows = duckdb.connect(database=":memory:").execute(sql, (pattern,)).fetchall()
        return tuple(str(row[0]) for row in rows)

    def validate_region_districts(
        self,
        regions: tuple[str, ...],
        districts: tuple[str, ...],
    ) -> None:
        """Reject district filters that cannot occur inside selected regions."""
        if not regions or not districts:
            return
        valid = set(self.districts(regions))
        invalid = set(districts) - valid
        if invalid:
            message = "district not present in selected regions: " + ", ".join(
                sorted(invalid)
            )
            raise ValueError(message)
