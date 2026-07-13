# Phase 2.5 Category Profile Evidence

## Scope check

- Implemented cohort-relevant category profiling only.
- Did not implement Phase 3 cohort sampler, Streamlit UI, response engines, LLM calls, or experiment runner.

## Commands run

```bash
.venv/bin/python -m pytest tests/test_category_profile.py
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/scl-profile-categories data/raw/ko_KR.parquet --output-dir outputs/data_inspection --top-n 50
.venv/bin/ruff format .
.venv/bin/ruff format --check .
.venv/bin/ruff check .
.venv/bin/python -m pytest
```

## Results

- Ruff format/check: passed.
- Pytest: `5 passed`.
- CLI outputs:
  - `outputs/data_inspection/category_profiles.json`
  - `outputs/data_inspection/category_profiles.csv`
  - `docs/column_profile.md`

## Raw data safety

- `data/raw/ko_KR.parquet` remained ignored by Git.
- File metadata after Phase 2.5: `2854775231` bytes, modified `Jul 13 13:52:43 2026`.
- No forbidden eager-load pattern for raw Parquet was found in source, tests, docs, or config.
- Name/address columns were not part of the profiling target list and were not written to profile outputs.

## Caveat

The generated profiles describe distributions inside a synthetic dataset only; they are not Korean population statistics.
