# Phase 3 Cohort Filter and Seeded Sampler Evidence

Implemented a DuckDB-backed cohort sampler for `data/raw/ko_KR.parquet`.

## User-facing surface

- `scl-cohort options`
- `scl-cohort districts`
- `scl-cohort occupations`
- `scl-cohort count`
- `scl-cohort sample`

## Safety properties

- Uses `uuid` as the Persona ID.
- Does not modify `data/raw/ko_KR.parquet`.
- Uses DuckDB projection/filter queries rather than loading the full raw Parquet
  into memory.
- Preview/sample exports exclude name/address fields and narrative persona text.
- Deterministic sampling uses `ORDER BY md5(uuid || '|' || seed)`.

## Verification

See the latest assistant report for exact gate outputs and raw smoke-test counts.
