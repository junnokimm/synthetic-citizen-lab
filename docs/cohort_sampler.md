# Phase 3 Cohort Sampler

`scl-cohort` counts and samples synthetic-persona cohorts from the immutable raw
Parquet file without loading the full dataset into memory.

## Commands

```bash
.venv/bin/scl-cohort options data/raw/ko_KR.parquet --column region
.venv/bin/scl-cohort districts data/raw/ko_KR.parquet --region 서울
.venv/bin/scl-cohort occupations data/raw/ko_KR.parquet --search 자영
.venv/bin/scl-cohort count data/raw/ko_KR.parquet --region 서울 --sex 여자 --age-min 40 --age-max 60
.venv/bin/scl-cohort sample data/raw/ko_KR.parquet --config examples/cohort_healthcare.json --output-dir outputs/cohorts
```

Inline filters may be repeated for OR-within-field semantics, for example
`--region 서울 --region 경기`. Different fields are combined with AND.

## Determinism

The sampler uses `uuid` as the Persona ID and sorts matching candidates with
`md5(uuid || '|' || seed)` before applying `LIMIT sample_size`. The same source
file, filter, sample size, and seed produce the same `sample_ids.csv` order.

## Output safety

Each saved cohort writes:

- `cohort.json`: source fingerprint, canonical filter JSON, matching count,
  sampling spec, and sampled IDs.
- `sample_ids.csv`: one `uuid` column.
- `sample_preview.csv`: safe preview columns only.

Preview/export defaults exclude name/address fields and narrative persona text.
