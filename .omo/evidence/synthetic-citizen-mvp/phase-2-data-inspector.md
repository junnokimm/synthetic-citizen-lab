# Phase 2 Data Inspector Evidence

## Scope check

- Implemented safe Parquet inspection only.
- Did not implement Streamlit UI, cohort sampler, response engines, LLM calls, or experiment runner.

## Commands run

```bash
.venv/bin/ruff format --check .
.venv/bin/ruff check .
.venv/bin/python -m pytest
.venv/bin/scl-inspect-data data/raw/ko_KR.parquet --output-dir outputs/data_inspection --sample-limit 5
.venv/bin/python -c "import synthetic_citizen_lab; print(synthetic_citizen_lab.__version__)"
```

## Results

- Ruff format: passed.
- Ruff check: passed.
- Pytest: `3 passed`.
- Import smoke: `0.1.0`.
- CLI outputs:
  - `outputs/data_inspection/inspection.json`
  - `outputs/data_inspection/data_dictionary.md`
  - `docs/data_dictionary.md`

## Raw data safety

- `data/raw/ko_KR.parquet` remained ignored by Git.
- File metadata after Phase 2: `2854775231` bytes, modified `Jul 13 13:52:43 2026`.
- No forbidden eager-load pattern for raw Parquet was found in source, tests, docs, or config.

## Raw inspection summary

- Rows: `1000000`
- Columns: `51`
- Row groups: `72`
- SHA-256: `8128b83c300c0f9f128580f6a5f0aafadf9b87c4fb9a6fff7ad8c141be320332`

## Phase 3 readiness

- Ready for Phase 3 after research-team review of column mapping questions.
- Data dictionary remains a draft; inferred categories are not confirmed semantics.
