# 합성 시민 Agent 기반 정책 반응 가상 실험 환경

Research MVP for exploring how Korean synthetic persona cohorts respond to policy
and public-service scenario explanations under controlled prompt, model,
temperature, seed, and repeat conditions.

## Non-claim

This project does **not** predict real citizen opinion, real policy acceptance
rates, election outcomes, or representative population projections. It is an
exploratory pretest tool for synthetic-persona response patterns and potential
acceptance barriers under explicitly configured experimental conditions.

## Phase 1 status

This repository currently contains only the Python project foundation:

- installable `src/synthetic_citizen_lab` package
- `pyproject.toml` with initial runtime and dev dependencies
- pytest and ruff configuration
- package import smoke test
- `.env.example`

Phase 2 adds safe raw Parquet inspection:

```bash
.venv/bin/scl-inspect-data data/raw/ko_KR.parquet --output-dir outputs/data_inspection --sample-limit 5
```

This writes `outputs/data_inspection/inspection.json` and refreshes
`docs/data_dictionary.md` as a non-authoritative draft.

Phase 2.5 profiles cohort-relevant categories and narrative length statistics:

```bash
.venv/bin/scl-profile-categories data/raw/ko_KR.parquet --output-dir outputs/data_inspection --top-n 50
```

This writes `outputs/data_inspection/category_profiles.json`,
`outputs/data_inspection/category_profiles.csv`, and `docs/column_profile.md`.

The following are intentionally **not** implemented yet:

- Streamlit dashboard
- cohort filtering
- response engines or LLM calls
- experiment runner and exports

## Data safety rules

- Treat `data/raw/ko_KR.parquet` as immutable source data.
- Never commit raw persona data, generated samples, local databases, or `.env`
  files.
- Do not load the full raw Parquet into memory. In later phases, inspect metadata
  and small previews through PyArrow or DuckDB projection, filter, and `LIMIT`
  queries.
- Do not write derived artifacts into `data/raw/`.

## Setup

Create and activate a local virtual environment, then install the package and
development tools:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e '.[dev]'
```

## Verification

```bash
.venv/bin/ruff check .
.venv/bin/python -m pytest
.venv/bin/python -c "import synthetic_citizen_lab; print(synthetic_citizen_lab.__version__)"
```

All commands must pass without an API key.
