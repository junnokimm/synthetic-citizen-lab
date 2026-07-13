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

Phase 3 adds safe cohort counting and deterministic seeded sampling:

```bash
.venv/bin/scl-cohort options data/raw/ko_KR.parquet --column region
.venv/bin/scl-cohort districts data/raw/ko_KR.parquet --region 서울
.venv/bin/scl-cohort occupations data/raw/ko_KR.parquet --search 자영
.venv/bin/scl-cohort count data/raw/ko_KR.parquet --region 서울 --sex 여자 --age-min 40 --age-max 60
.venv/bin/scl-cohort sample data/raw/ko_KR.parquet --config examples/cohort_healthcare.json --output-dir outputs/cohorts
```

Sampling uses `uuid` as the Persona ID and orders candidates by
`md5(uuid || '|' || seed)`, so the same source fingerprint, filter, sample size,
and seed return the same ID list in the same order. Cohort exports include
`cohort.json`, `sample_ids.csv`, and `sample_preview.csv`. Preview/export columns
exclude direct name/address fields and narrative persona text by default.

The following are intentionally **not** implemented yet:

- Streamlit dashboard
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
