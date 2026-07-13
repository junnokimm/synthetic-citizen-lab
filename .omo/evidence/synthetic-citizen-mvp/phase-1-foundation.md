# Phase 1 Foundation Evidence

## Scope check

- Implemented only project foundation files: Python metadata, package skeleton, README, `.env.example`, `AGENTS.md`, and import smoke test.
- Did not implement Parquet analysis, Streamlit UI, cohort sampling, response engines, LLM calls, or experiment runner.

## Commands run

```bash
brew install python@3.11
/opt/homebrew/bin/python3.11 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/ruff check .
.venv/bin/python -m pytest
.venv/bin/python -c "import synthetic_citizen_lab; print(synthetic_citizen_lab.__version__)"
```

## Results

- Dependency install: passed.
- Ruff: `All checks passed!`
- Pytest: `1 passed` on Python 3.11.15.
- Import smoke: printed `0.1.0`.

## Data safety check

- `data/raw/ko_KR.parquet` remained ignored by Git.
- File metadata after Phase 1: `2854775231` bytes, modified `Jul 13 13:52:43 2026`.
- No forbidden eager-load pattern for `data/raw/ko_KR.parquet` was found.

## Phase 2 readiness

- Ready for Phase 2 after review.
- Phase 2 must start with metadata/schema inspection only and must not load the full raw Parquet into memory.
