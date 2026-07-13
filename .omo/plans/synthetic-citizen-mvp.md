# synthetic-citizen-mvp - Work Plan

## TL;DR (For humans)

**What you'll get:** 한국형 합성 페르소나 Parquet를 안전하게 탐색하고, cohort를 만들고, 정책 설명안별 mock agent 반응을 반복 실행·비교·내보낼 수 있는 연구용 MVP를 구축한다.

**Why this approach:** 2.7GB 원본 Parquet를 전체 메모리에 올리지 않기 위해 DuckDB/Parquet metadata 중심으로 접근하고, Streamlit으로 연구자가 직접 cohort·정책 설명안·반복 조건을 조정하는 로컬 실험 UI를 만든다.

**What it will NOT do:** 실제 시민 여론·수용률을 예측하거나 대표성 있는 projection을 주장하지 않는다. 원본 `data/raw/ko_KR.parquet`를 수정하거나 Git에 포함하지 않는다. 첫 MVP에서는 agent 간 토론, 확산 모델, 인증, 운영 서버, 지식그래프를 만들지 않는다.

**Effort:** Large
**Risk:** Medium - 원본 Parquet schema가 아직 미확인이고, 대용량 데이터 안전 처리와 연구적 non-claim 문구가 계속 검증되어야 한다.
**Decisions to sanity-check:** persona column mapping, 소득/건강 taxonomy, 설명안 A/B/C 비교 축, mock scoring scale, 안정성 지표 정의, Live OpenAI 모델/temperature 범위.

Your next move: 이 계획으로 실행하려면 `$start-work`를 요청한다. 실행 전 고정밀 계획 리뷰를 먼저 원하면 “review first”라고 요청한다.

---

> TL;DR (machine): Large Python/Streamlit/DuckDB MVP; build safe Parquet inspection, cohort sampling, mock/live response engine interface, experiment runner, comparison dashboard, exports, and pytest coverage without claiming real public-opinion prediction.

## Scope

### Project goal and non-claim

- 프로젝트명: **합성 시민 Agent 기반 정책 반응 가상 실험 환경**.
- 목표: 한국형 합성 페르소나 데이터를 활용해 정책 및 공공서비스 시나리오에 대한 시민 cohort별 초기 반응을 생성하고, 정책 설명안별 차이와 반복 실행 안정성을 비교할 수 있는 연구용 실험 환경을 구현한다.
- Non-claim: 이 시스템은 실제 시민 여론, 정책 수용률, 선거/정책 결과, 대표성 있는 인구 projection을 예측한다고 주장하지 않는다. 설정된 합성 페르소나, prompt, model, temperature, seed 조건에서 생성되는 반응 패턴과 잠재적 수용 장벽을 탐색하는 **pretest 도구**다.

### Repository facts to preserve

- `AGENTS.md`: 현재 소스/manifest/CI가 거의 없고 stack 추정을 금지한다고 적혀 있다. Phase 1에서 실제 stack과 data safety 지침으로 갱신한다.
- `.gitignore`: `.env*`, Python cache, `data/raw/*`, `data/sample/*`, `outputs/*`, local DB를 무시한다. `data/raw/.gitkeep`, `data/sample/.gitkeep`, `outputs/.gitkeep`는 추적된다.
- `data/raw/ko_KR.parquet`: Apache Parquet, 약 2.7GB, Git ignored. 원본 불변.
- 현재 repo에는 `docs/`, `src/`, `tests/` 디렉터리가 있으나 구현 파일은 없다.
- 현재 로컬 Python에는 `pyarrow`와 `duckdb`가 설치되어 있지 않은 상태가 확인되었다. 의존성 설치/설정은 Phase 1 실행 시 수행한다.

### Must have

- Persona 데이터 파일 탐색 및 schema/metadata 분석.
- Persona 데이터 사전 생성: 원본 column과 내부 표준 persona field mapping.
- 연령, 성별, 지역, 직업, 소득, 건강 상태 기반 cohort filter.
- seed를 저장하는 재현 가능한 표본 추출.
- 정책 시나리오 입력.
- 정책 설명안 A/B/C 직접 입력 및 template 기반 생성 hook.
- Persona 정보 조건 선택:
  - P1: 인구통계·사회경제 속성.
  - P2: P1 + 건강·성격 등 도메인 속성.
  - P3: P2 + 서술형 Persona.
- Mock Response Engine.
- 이후 OpenAI API를 연결할 수 있는 Live Response Engine interface와 placeholder.
- 구조화된 agent 반응 저장.
- cohort 및 설명안별 결과 비교.
- 실험 조건, prompt version, model, temperature, seed, repeat number 저장.
- 반복 실행 변동성 확인.
- 간단한 Streamlit dashboard와 JSON/CSV 결과 export.
- pytest 기반 테스트.

### Must NOT have (guardrails, anti-slop, scope boundaries)

- 실제 소스 코드나 프로젝트 설정 파일은 이 계획 작성 단계에서 수정하지 않는다.
- `data/raw/ko_KR.parquet`를 수정, 재저장, 이동, Git add, commit하지 않는다.
- 대용량 원본 전체를 `pandas.read_parquet("data/raw/ko_KR.parquet")`처럼 eager load하지 않는다.
- 전체 합성 인구에 대해 LLM 호출하지 않는다.
- 실제 한국 인구의 수용률로 해석되는 projection, prediction, acceptance-rate claim을 만들지 않는다.
- Agent 간 토론, 네트워크 상호작용, 여론 확산, 집단 극화, 인증, 복잡한 운영 서버, 분산처리, 지식그래프는 제외한다.
- 원본 persona raw 전체를 기본 export하지 않는다. PII/민감정보 가능성을 가정하고 최소 표시한다.

### Recommended stack

- Python 3.11+ 또는 3.12.
- Streamlit: 연구용 로컬 dashboard.
- DuckDB: Parquet 직접 query, filter, aggregation, sampling.
- PyArrow: Parquet footer/schema/metadata inspection.
- Pydantic v2: experiment spec, policy, response, export schema validation.
- Plotly: cohort/explanation/repeat 비교 시각화.
- pandas: 작은 결과 table과 CSV export 전용. 원본 전체 read 금지.
- pytest: unit/integration tests.
- ruff: lint/format.

## Verification strategy

> Zero human intervention - all verification is agent-executed, except phase review gates where the worker reports evidence and waits for user approval before continuing if instructed.

- Test decision: tests-after for MVP scaffolding, then TDD for data access, sampling, prompt builder, engines, exports. Framework: pytest.
- Static verification: `ruff check .`, `ruff format --check .` once Phase 1 defines tooling.
- Unit tests:
  - Pydantic model validation.
  - cohort filter query generation.
  - persona field mapping validation.
  - seed sampling determinism.
  - P1/P2/P3 context inclusion/exclusion.
  - MockResponseEngine deterministic output.
  - structured JSON/CSV export schema.
- Integration tests:
  - Generate a tiny fixture Parquet in a temp directory; never use the 2.7GB raw file as a test fixture.
  - Run DuckDB schema/query/sample path against fixture.
  - Run mock experiment matrix and verify metadata/result persistence.
- Data safety tests:
  - Grep/AST check to reject direct eager full-load call patterns against `data/raw/ko_KR.parquet`.
  - Inspector smoke test uses metadata/schema or `LIMIT`, not full load.
  - Missing `duckdb`/`pyarrow` error path is clear.
- Streamlit smoke QA:
  - `streamlit run src/synthetic_citizen_lab/dashboard/app.py` after dashboard exists.
  - Agent-executed browser smoke: open app, verify Data Overview, Cohort Builder, Scenario Builder, Experiment Runner, Results, Export screens render.
- Evidence path convention: `.omo/evidence/synthetic-citizen-mvp/phase-<N>-<name>.md` with exact commands, outputs, screenshots where relevant, and pass/fail notes.

## Execution strategy

### Parallel execution waves

- Wave 1: Phase 1 foundation. Single dependency root; do not parallelize until package/tooling exists.
- Wave 2: Phase 2 data inspector and Phase 3 dictionary/cohort models can partially overlap after core config and dependencies exist.
- Wave 3: Phase 4 sampler and Phase 5 scenario/prompt/engine can partially overlap once persona models are stable.
- Wave 4: Phase 6 runner/storage depends on sampler and engines.
- Wave 5: Phase 7 dashboard depends on end-to-end service APIs but can initially use mock fixtures.
- Final wave: plan compliance, code quality, data safety, and scope fidelity reviews in parallel.

### Dependency matrix

| Todo | Depends on | Blocks | Can parallelize with |
| --- | --- | --- | --- |
| 1 Phase 1 foundation | None | All later phases | None initially |
| 2 Phase 2 safe data inspector | 1 | 3, 4, 7 Data Overview | 3 model sketch after schema contract exists |
| 3 Phase 3 dictionary/cohort filter | 1, partial 2 | 4, 6, 7 Cohort Builder | 5 scenario/prompt work |
| 4 Phase 4 reproducible sampler | 2, 3 | 6, 7 Experiment Setup | 5 engines |
| 5 Phase 5 policy/prompt/engines | 1, 3 persona model contract | 6, 7 Scenario/Run UI | 4 sampler |
| 6 Phase 6 experiment runner/storage | 4, 5 | 7 Results/Export UI | Early 7 UI skeleton with fixtures |
| 7 Phase 7 dashboard/comparison/export | 2, 3, 4, 5, 6 | Final verification | None |

### Phase review procedure before moving on

After every Phase 1~7, the worker must stop and record a review note before continuing:

1. Plan compliance check: confirm phase deliverables match this plan and no excluded scope was added.
2. Data safety check: confirm raw Parquet was not modified, copied into Git-tracked paths, or fully loaded.
3. Test/evidence check: run the phase-specific commands and save evidence under `.omo/evidence/synthetic-citizen-mvp/`.
4. Research non-claim check: confirm UI/docs/export text does not imply real public opinion prediction.
5. Dirty worktree check: show `git status --short --ignored` and explain expected ignored/raw files.
6. Decision log update: add newly discovered schema constraints or research-team decisions to docs or issue notes as appropriate.
7. Continue only after the review note is complete. If a phase changes architecture, pause for user approval before moving to the next phase.

## Todos

> Implementation + Test = ONE todo. Never separate.
<!-- APPEND TASK BATCHES BELOW THIS LINE WITH edit/apply_patch - never rewrite the headers above. -->

- [ ] 1. Phase 1 - Establish Python project foundation and repo guidance
  What to do / Must NOT do: Create the Python package skeleton, `pyproject.toml`, dependency groups, pytest/ruff config, README, `.env.example`, and update `AGENTS.md` with verified stack and data-safety rules. Must NOT inspect or transform raw data beyond existing file metadata in this phase. Must NOT start Streamlit feature work before tooling imports/tests work.
  Parallelization: Wave 1 | Blocked by: None | Blocks: all later phases
  References (executor has NO interview context - be exhaustive): `AGENTS.md`, `.gitignore`, current repo folders `docs/`, `src/`, `tests/`, `data/raw/ko_KR.parquet`; user requirements in this plan Scope.
  Acceptance criteria (agent-executable): `python -m pytest` runs with at least one smoke test; `ruff check .` and `ruff format --check .` run; package import smoke passes; README states project goal and non-claim; `AGENTS.md` states raw data immutable and no full Parquet load.
  QA scenarios (name the exact tool + invocation): happy: run `python -m pytest`, `ruff check .`, `python -c "import synthetic_citizen_lab"`; failure: temporarily simulate missing optional data dependency in tests or document clear import error behavior. Evidence `.omo/evidence/synthetic-citizen-mvp/phase-1-foundation.md`.
  Review before next phase: apply the seven-step phase review procedure, especially checking no raw data operation occurred.
  Commit: Y when user requests commits | `chore(project): configure python research mvp foundation`

- [ ] 2. Phase 2 - Implement safe Parquet metadata inspector
  What to do / Must NOT do: Implement data inspection functions that read file size, format, Parquet row count, column count, row group count, schema, and tiny `LIMIT` preview. Use PyArrow footer and/or DuckDB `DESCRIBE SELECT * FROM read_parquet(...)`. Must NOT call full-file pandas read on `data/raw/ko_KR.parquet`. Must NOT write derived data into `data/raw/`.
  Parallelization: Wave 2 | Blocked by: Phase 1 | Blocks: Phase 3, Phase 4, Phase 7 Data Overview
  References (executor has NO interview context - be exhaustive): `data/raw/ko_KR.parquet` is 2.7GB Apache Parquet and ignored; `.gitignore` raw/generated rules; Scope data safety rules.
  Acceptance criteria (agent-executable): inspector returns metadata for a tiny fixture Parquet in tests; when optional dependencies are missing it raises actionable errors; against real `data/raw/ko_KR.parquet`, smoke command prints schema/metadata without materializing all rows; no code pattern `pd.read_parquet("data/raw/ko_KR.parquet")` exists.
  QA scenarios (name the exact tool + invocation): happy: run `python -m pytest tests/test_data_inspector.py`; real-data smoke: run a CLI/module command that prints only metadata and first 5 rows; failure: missing file path returns clear error. Evidence `.omo/evidence/synthetic-citizen-mvp/phase-2-data-inspector.md`.
  Review before next phase: confirm raw file mtime/checksum did not change and no raw Parquet copy appears in tracked files.
  Commit: Y when user requests commits | `feat(data): inspect parquet metadata safely`

- [ ] 3. Phase 3 - Build persona dictionary and cohort filter layer
  What to do / Must NOT do: Create Pydantic models for persona field mapping and cohort filters. Implement mapping from source columns to internal fields: age, gender, region, job, income, health_status, personality/domain attributes, narrative. Implement DuckDB SQL query builder for cohort matching count and filtered relation. Must NOT hard-code unverified column names as permanent truth; defaults must come from inspector/dictionary output.
  Parallelization: Wave 2 | Blocked by: Phase 1 and Phase 2 schema contract | Blocks: Phase 4, Phase 6, Phase 7 Cohort Builder
  References (executor has NO interview context - be exhaustive): RQ1/RQ2/RQ3 in user brief; Scope Must have persona dictionary and cohort filters; Phase 2 schema output.
  Acceptance criteria (agent-executable): tests validate mapping model, unknown-column rejection, SQL generation for age/gender/region/job/income/health filters, empty-result handling, and matching-count query against fixture Parquet.
  QA scenarios (name the exact tool + invocation): happy: `python -m pytest tests/test_persona_dictionary.py tests/test_cohort_filter.py`; failure: mapping references non-existent column and raises validation error. Evidence `.omo/evidence/synthetic-citizen-mvp/phase-3-dictionary-cohort.md`.
  Review before next phase: research team decision log lists unresolved taxonomy issues discovered from schema, especially income and health fields.
  Commit: Y when user requests commits | `feat(data): add persona dictionary and cohort filters`

- [ ] 4. Phase 4 - Implement reproducible seeded sampling
  What to do / Must NOT do: Implement seed-based sampling over filtered DuckDB queries, persist `SamplingSpec`, selected persona IDs, source file fingerprint, schema hash, filter query, sample size, and timestamp. Store generated samples under ignored paths such as `data/sample/` or `outputs/`, never `data/raw/`. Must NOT sample by loading all raw rows into Python memory.
  Parallelization: Wave 3 | Blocked by: Phase 2 and Phase 3 | Blocks: Phase 6 and Phase 7 Experiment Setup
  References (executor has NO interview context - be exhaustive): Scope reproducible sampling requirement; `.gitignore` sample/output rules; data safety rules.
  Acceptance criteria (agent-executable): same seed + same filter returns same ordered persona IDs; different seed changes sample order or membership where possible; sample size greater than match count fails clearly; sampling metadata is saved and reloadable.
  QA scenarios (name the exact tool + invocation): happy: `python -m pytest tests/test_sampler.py`; failure: request sample size larger than filtered count and assert explicit error. Evidence `.omo/evidence/synthetic-citizen-mvp/phase-4-sampling.md`.
  Review before next phase: verify sample artifacts are ignored or intentionally tracked only when tiny fixtures; verify raw file unchanged.
  Commit: Y when user requests commits | `feat(data): add reproducible persona sampling`

- [ ] 5. Phase 5 - Add policy scenario, prompt builder, and response engines
  What to do / Must NOT do: Create Pydantic models for policy scenarios, explanation variants A/B/C, persona info conditions P1/P2/P3, prompt versions, and structured agent response. Implement prompt/context builder that includes only allowed fields per P1/P2/P3. Implement `ResponseEngine` interface, deterministic `MockResponseEngine`, and `LiveResponseEngine` placeholder that is disabled unless configured. Must NOT make real OpenAI calls by default. Must NOT include narrative in P1/P2.
  Parallelization: Wave 3 | Blocked by: Phase 1 and Phase 3 persona model contract | Blocks: Phase 6 and Phase 7 Scenario/Run UI
  References (executor has NO interview context - be exhaustive): User-specified P1/P2/P3 definitions; MVP includes Mock engine and future Live interface; non-claim requirement.
  Acceptance criteria (agent-executable): tests prove P1 excludes health/personality/narrative as defined, P2 includes domain fields but excludes narrative, P3 includes narrative, mock engine deterministic by seed, live engine raises clear not-configured error without API key.
  QA scenarios (name the exact tool + invocation): happy: `python -m pytest tests/test_prompt_builder.py tests/test_mock_engine.py`; failure: attempt LiveResponseEngine without configuration and assert no network call occurs. Evidence `.omo/evidence/synthetic-citizen-mvp/phase-5-prompts-engines.md`.
  Review before next phase: verify prompt templates and UI copy include exploratory/non-predictive language.
  Commit: Y when user requests commits | `feat(experiment): add policy prompts and response engines`

- [ ] 6. Phase 6 - Implement experiment runner, result storage, and comparison metrics
  What to do / Must NOT do: Build experiment matrix over cohort sample × explanation A/B/C × persona info condition × repeat index. Save structured responses with experiment_id, cohort_id, persona_id, explanation_id, prompt_version, model, temperature, seed, repeat index, engine, and raw/parsed response. Implement JSONL/JSON and CSV export plus optional local DuckDB result store. Implement comparison and stability metrics: support distribution, concern frequency, benefit frequency, response length, repeat variance, concern overlap. Must NOT interpret metrics as real public opinion.
  Parallelization: Wave 4 | Blocked by: Phase 4 and Phase 5 | Blocks: Phase 7 Results/Export UI
  References (executor has NO interview context - be exhaustive): RQ2/RQ3/RQ4; MVP requirements 10-13; non-claim and export constraints.
  Acceptance criteria (agent-executable): fixture experiment run produces expected number of records; every record contains required metadata; JSON/CSV export validates; failed response becomes error record; stability metrics computed on fixture repeats.
  QA scenarios (name the exact tool + invocation): happy: `python -m pytest tests/test_experiment_runner.py tests/test_exports.py tests/test_comparison.py`; failure: mock engine raises for one persona and runner stores error without aborting whole experiment. Evidence `.omo/evidence/synthetic-citizen-mvp/phase-6-runner-storage.md`.
  Review before next phase: inspect sample exported JSON/CSV to ensure no forbidden projection language and no default full raw persona dump.
  Commit: Y when user requests commits | `feat(experiment): run and store structured mock experiments`

- [ ] 7. Phase 7 - Build Streamlit dashboard and end-to-end MVP flow
  What to do / Must NOT do: Implement Streamlit dashboard with Data Overview, Persona Dictionary, Cohort Builder, Policy Scenario/Explanation, Experiment Setup, Run & Monitor, Results Comparison, Stability, and Export views. Use cached metadata/query helpers carefully; never cache or display the full raw dataset. Include visible non-claim text in the app and exported metadata.
  Parallelization: Wave 5 | Blocked by: Phases 2-6 | Blocks: Final verification
  References (executor has NO interview context - be exhaustive): MVP requirement 14 dashboard/export; screen/user-flow section in approved plan; Streamlit caching/session-state docs are appropriate for small derived data, not full raw data.
  Acceptance criteria (agent-executable): app launches; Data Overview shows metadata not full raw table; cohort/sample workflow works on fixture and optionally real metadata; mock experiment can run; results charts render; JSON/CSV export works; app text includes non-claim.
  QA scenarios (name the exact tool + invocation): happy: run `streamlit run src/synthetic_citizen_lab/dashboard/app.py` and perform agent-executed browser smoke through all major screens; failure: missing raw file produces actionable UI message. Evidence `.omo/evidence/synthetic-citizen-mvp/phase-7-dashboard.md` plus screenshot paths.
  Review before next phase: complete full seven-step phase review and confirm all MVP inclusions are covered, exclusions remain excluded, and raw data is safe.
  Commit: Y when user requests commits | `feat(ui): add research mvp dashboard`

## Final verification wave

> Runs in parallel after ALL todos. ALL must APPROVE. Surface results and wait for the user's explicit okay before declaring complete.

- [ ] F1. Plan compliance audit
  - Verify every Must have is implemented or explicitly deferred with user approval.
  - Verify every Must NOT have is absent.
  - Evidence: `.omo/evidence/synthetic-citizen-mvp/final-plan-compliance.md`.
- [ ] F2. Code quality review
  - Run `ruff check .`, `ruff format --check .`, `python -m pytest`.
  - Inspect for oversized modules, untyped public APIs, broad `Any` overuse, and hard-coded unverified raw schema assumptions.
  - Evidence: `.omo/evidence/synthetic-citizen-mvp/final-code-quality.md`.
- [ ] F3. Agent-executed hands-on QA
  - Launch Streamlit app, complete the MVP flow with fixture data and mock engine, export JSON/CSV, and capture screenshots/logs.
  - Evidence: `.omo/evidence/synthetic-citizen-mvp/final-hands-on-qa.md`.
- [ ] F4. Scope fidelity and data safety audit
  - Confirm `data/raw/ko_KR.parquet` remains ignored and unchanged.
  - Search for forbidden full-load patterns against raw Parquet.
  - Verify README/dashboard/export non-claim language.
  - Evidence: `.omo/evidence/synthetic-citizen-mvp/final-scope-data-safety.md`.

## Commit strategy

- This planning request does not authorize commits. Do not commit the plan unless the user explicitly asks.
- During future implementation, prefer one commit per phase when each phase is independently reviewable; split further if a phase touches unrelated concerns.
- Never commit `data/raw/ko_KR.parquet`, generated large samples, `.env`, local databases, or `.omo/evidence` unless explicitly requested.
- Before any commit: inspect `git status`, `git diff`, and `git diff --staged`; stage only intended source/docs/config/test files.

## Success criteria

- A researcher can run the local app, inspect raw Parquet metadata safely, build a cohort, create or enter policy explanations A/B/C, run mock agent responses with repeat/seed metadata, compare results, and export JSON/CSV.
- The system records experiment condition, prompt version, model, temperature, seed, repeat number, cohort, explanation variant, persona info condition, and engine for every response.
- Same seed/filter/sample specification is reproducible.
- Tests cover data inspector, cohort filter, sampler, prompt builder, mock engine, experiment runner, exports, and safety edge cases.
- The raw 2.7GB Parquet is never modified, committed, or fully loaded into memory.
- Docs/UI/exports clearly state the system is an exploratory synthetic pretest environment, not a real public opinion or policy acceptance predictor.
- Each phase has a saved review note and evidence before moving to the next phase.

## Research-team decisions still unresolved

- Persona ID: use source ID if present; otherwise define stable hash inputs.
- Income handling: numeric range vs categorical bands; decide official bands for analysis.
- Health status taxonomy: preserve raw categories or normalize into research-defined groups.
- Personality/domain attributes: decide which source fields belong in P2.
- Narrative truncation: maximum length and redaction policy for P3.
- Explanation A/B/C comparison axis: e.g. benefit-focused, cost-focused, procedure/safety-focused, rights/equity-focused.
- Mock scoring scale: recommended `support_level` 1-5, but decide whether neutral/conditional acceptance is separate.
- Stability metrics: choose primary metric among support variance, concern-set overlap, response-length variance, semantic similarity, or composite index.
- Live engine defaults: OpenAI model, temperature range, retry/rate-limit policy, and whether seed is supported/meaningful for selected model.
- Export privacy: decide whether exports include raw persona fields, derived fields only, or persona IDs plus aggregated attributes.
- Data dictionary ownership: decide who reviews and approves source-column mapping after Phase 2/3.
