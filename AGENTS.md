# Repository Notes

- This is a Python research MVP for synthetic-citizen policy-response pretests, not a production service and not a real public-opinion prediction system.
- Package source lives under `src/synthetic_citizen_lab`; tests live under `tests` and run with pytest.
- Use the local venv commands from `README.md`: `.venv/bin/ruff check .`, `.venv/bin/python -m pytest`, and `.venv/bin/python -c "import synthetic_citizen_lab"`.
- Safe raw data inspection CLI: `.venv/bin/scl-inspect-data data/raw/ko_KR.parquet --output-dir outputs/data_inspection --sample-limit 5`.
- Safe category profiling CLI: `.venv/bin/scl-profile-categories data/raw/ko_KR.parquet --output-dir outputs/data_inspection --top-n 50`.
- `data/raw/ko_KR.parquet` is immutable source data. Do not modify, move, re-save, stage, or commit it.
- Never load the full raw Parquet into memory. Data work must use PyArrow/DuckDB metadata, projection, filters, sampling, and small `LIMIT` previews.
- Current scope still excludes Streamlit UI, cohort sampler, and LLM/API calls.
- `.env` and `.env.*` stay local; tests must pass without API keys.
- `.omo/` is local OpenCode planning/session state, not project source or repo guidance unless the user explicitly asks to inspect a plan.
