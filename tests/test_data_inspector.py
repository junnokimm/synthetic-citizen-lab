from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from synthetic_citizen_lab.cli import main
from synthetic_citizen_lab.data.inspector import inspect_parquet


def _write_fixture_parquet(path: Path) -> None:
    table = pa.table(
        {
            "persona_id": pa.array(["p1", "p2", "p3"]),
            "age": pa.array([25, 40, None], type=pa.int64()),
            "gender": pa.array(["female", "male", "female"]),
            "name": pa.array(["Kim A", "Lee B", "Park C"]),
            "address": pa.array(["Seoul detail", None, "Busan detail"]),
            "openness": pa.array([0.5, 0.7, None], type=pa.float64()),
            "persona_story": pa.array(["story one", "story two", "story three"]),
        }
    )
    pq.write_table(table, path, row_group_size=2)


def test_inspect_parquet_reads_metadata_and_masks_samples(tmp_path: Path) -> None:
    # Given: a tiny Parquet fixture with likely identifying columns.
    parquet_path = tmp_path / "fixture.parquet"
    output_dir = tmp_path / "inspection"
    _write_fixture_parquet(parquet_path)

    # When: inspecting the fixture through the Phase 2 inspector.
    result = inspect_parquet(parquet_path, output_dir=output_dir, sample_limit=2)

    # Then: metadata, null statistics, masked sample, and output files exist.
    assert result.file.exists is True
    assert result.parquet.num_rows == 3
    assert result.parquet.num_columns == 7
    assert result.parquet.num_row_groups == 2
    assert result.columns[1].name == "age"
    assert result.columns[1].null_count == 1
    assert result.columns[1].null_ratio == 1 / 3
    assert result.sample_rows[0]["name"] == "***MASKED***"
    assert result.sample_rows[0]["address"] == "***MASKED***"
    assert "persona_id" in result.candidates.persona_id
    assert "age" in result.candidates.demographic
    assert "openness" in result.candidates.big_five
    assert "persona_story" in result.candidates.narrative
    assert result.json_path.exists()
    assert result.dictionary_path.exists()


def test_inspection_cli_writes_outputs_and_docs(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Given: a fixture Parquet and an isolated working directory.
    parquet_path = tmp_path / "fixture.parquet"
    _write_fixture_parquet(parquet_path)
    monkeypatch.chdir(tmp_path)

    # When: running the inspection CLI with an explicit output directory.
    exit_code = main((str(parquet_path), "--output-dir", "outputs/data_inspection"))

    # Then: machine JSON and review-oriented dictionary drafts are written.
    assert exit_code == 0
    assert (tmp_path / "outputs/data_inspection/inspection.json").exists()
    assert (tmp_path / "outputs/data_inspection/data_dictionary.md").exists()
    assert (tmp_path / "docs/data_dictionary.md").exists()
