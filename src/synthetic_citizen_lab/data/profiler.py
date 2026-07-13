"""DuckDB-backed category profiling for synthetic-persona Parquet data."""

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from synthetic_citizen_lab.data.profile_models import (
    CategoricalColumnProfile,
    CategoryProfileResult,
)
from synthetic_citizen_lab.data.profile_queries import (
    age_profile,
    available_columns,
    big_five_profiles,
    categorical_profiles,
    narrative_profiles,
    row_count,
)
from synthetic_citizen_lab.data.profile_targets import (
    PROFILE_CAVEAT,
)
from synthetic_citizen_lab.data.profile_writer import write_profile_artifacts

DEFAULT_TOP_N: Final[int] = 50


@dataclass(frozen=True, slots=True)
class ProfilePaths:
    """Output paths for a category profiling run."""

    json_path: Path
    csv_path: Path
    markdown_path: Path


def profile_parquet(
    parquet_path: Path,
    *,
    output_dir: Path,
    top_n: int = DEFAULT_TOP_N,
) -> CategoryProfileResult:
    """Profile configured columns using aggregate DuckDB queries."""
    source_path = parquet_path.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = ProfilePaths(
        json_path=output_dir / "category_profiles.json",
        csv_path=output_dir / "category_profiles.csv",
        markdown_path=Path("docs/column_profile.md"),
    )
    columns = available_columns(source_path)
    total_rows = row_count(source_path)
    categorical = categorical_profiles(source_path, columns, total_rows, top_n)
    big_five = big_five_profiles(source_path, columns)
    narrative = narrative_profiles(source_path, columns, total_rows)
    result = CategoryProfileResult(
        source_path=source_path,
        row_count=total_rows,
        caveat=PROFILE_CAVEAT,
        categorical=categorical,
        age=age_profile(source_path),
        big_five=big_five,
        narrative=narrative,
        income_bracket_order=_income_bracket_order(categorical),
        income_order_inferred="income_bracket" in categorical,
        direct_ui_fields=tuple(
            column for column, profile in categorical.items() if profile.direct_ui_ready
        ),
        normalization_needed=tuple(
            column
            for column, profile in categorical.items()
            if not profile.direct_ui_ready
        ),
        json_path=paths.json_path,
        csv_path=paths.csv_path,
        markdown_path=paths.markdown_path,
    )
    write_profile_artifacts(result)
    return result


def _income_bracket_order(
    categorical: Mapping[str, CategoricalColumnProfile],
) -> tuple[str, ...]:
    profile = categorical.get("income_bracket")
    if profile is None:
        return ()
    values = {str(value.value) for value in profile.values}
    preferred_order = (
        "해당없음",
        "85만원미만",
        "85~150만원",
        "150~250만원",
        "250~350만원",
        "350~450만원",
        "450~550만원",
        "550~650만원",
        "650~800만원",
        "800~1000만원",
        "1000만원이상",
    )
    return tuple(value for value in preferred_order if value in values)
