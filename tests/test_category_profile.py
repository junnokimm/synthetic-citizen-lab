from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from synthetic_citizen_lab.data.profiler import profile_parquet
from synthetic_citizen_lab.profile_cli import main


def _write_profile_fixture(path: Path) -> None:
    table = pa.table(
        {
            "sex": pa.array(["female", "male", "female", "female"]),
            "region": pa.array(["Seoul", "Busan", "Seoul", "Jeju"]),
            "district": pa.array(["A", "B", "A", "C"]),
            "age": pa.array([19, 35, 67, 40], type=pa.int64()),
            "education_level": pa.array(["college", "high", "college", "grad"]),
            "economic_activity_status": pa.array(
                ["active", "inactive", "active", "active"]
            ),
            "income_bracket": pa.array(["low", "middle", "high", "middle"]),
            "bmi_status": pa.array(["normal", "normal", "high", "low"]),
            "openness": pa.array(["high", "medium", "low", "high"]),
            "persona": pa.array(
                ["same text", "same text", "other", "longer text here"]
            ),
        }
    )
    pq.write_table(table, path, row_group_size=2)


def test_profile_parquet_summarizes_categories_age_and_narratives(
    tmp_path: Path,
) -> None:
    # Given: a fixture Parquet with category, age, Big Five, and narrative fields.
    parquet_path = tmp_path / "fixture.parquet"
    output_dir = tmp_path / "profiles"
    _write_profile_fixture(parquet_path)

    # When: profiling the fixture with DuckDB aggregate queries.
    result = profile_parquet(parquet_path, output_dir=output_dir, top_n=2)

    # Then: profile artifacts contain bounded value counts and derived statistics.
    assert result.row_count == 4
    assert result.categorical["sex"].distinct_count == 2
    assert result.categorical["sex"].values[0].value == "female"
    assert result.categorical["sex"].values[0].count == 3
    assert result.age.minimum == 19
    assert result.age.maximum == 67
    assert result.big_five["openness"].numeric_parseable is False
    assert result.narrative["persona"].max_length == len("longer text here")
    assert result.narrative["persona"].duplicate_row_ratio == 0.25
    assert result.json_path.exists()
    assert result.csv_path.exists()
    assert result.markdown_path.exists()


def test_profile_cli_writes_profile_outputs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: a fixture Parquet and isolated working directory.
    parquet_path = tmp_path / "fixture.parquet"
    _write_profile_fixture(parquet_path)
    monkeypatch.chdir(tmp_path)

    # When: running the category profile CLI.
    exit_code = main((str(parquet_path), "--output-dir", "outputs/data_inspection"))

    # Then: JSON, CSV, and docs markdown outputs are written.
    assert exit_code == 0
    assert (tmp_path / "outputs/data_inspection/category_profiles.json").exists()
    assert (tmp_path / "outputs/data_inspection/category_profiles.csv").exists()
    assert (tmp_path / "docs/column_profile.md").exists()
