# synthetic-citizen-mvp - Work Plan

## TL;DR (For humans)

**What you'll get:** 기존의 안전한 Parquet 점검/프로파일링/코호트 샘플링 기반 위에, **backend/CLI-first 연구용 실험 MVP**를 추가한다. 이 MVP는 기존 cohort artifact를 재사용해 시나리오·질문을 저장하고, 결정론적 mock response를 실행하며, 반복 비교·제한된 후속질문·CSV/JSONL export까지 수행한다.

**Why this approach:** 현재 저장소의 강점은 이미 구현된 **안전한 원천데이터 접근**과 **재현 가능한 cohort 구성**이다. 따라서 UI나 실 API 연동보다 먼저, 실험 도메인 모델·저장 구조·실행 파이프라인을 정확히 고정하는 것이 가장 리스크가 낮고 PRD와도 잘 맞는다.

**What it will NOT do:** 첫 계획 범위에는 **Streamlit UI를 넣지 않는다.** **실제 LLM/API 호출도 넣지 않는다.** `data/raw/ko_KR.parquet`는 수정/이동/재저장/commit하지 않으며, 전체 메모리 적재도 하지 않는다. `PARAPHRASE`, 고급 NLI/LLM Judge, 자유형 멀티턴 인터뷰, 새로운 샘플링 알고리즘, 예측/추론 통계는 제외한다.

**Effort:** Large
**Risk:** Medium — 기존 cohort artifact와 새 실험 artifact를 매끄럽게 연결해야 하고, raw Parquet 안전 제약을 모든 새 기능에 관통시켜야 한다.
**Decisions locked:** backend/CLI-first, `ORIGINAL + SAME_QUESTION_REPEAT` only, TDD for new domain logic, file-backed JSON/JSONL+CSV storage, mock-only response generation for this MVP.

Your next move: 이 계획대로 실행하려면 `$start-work`를 요청한다. 실행 전 더 엄격한 계획 리뷰를 원하면 `review first`라고 말하면 된다.

---

> TL;DR (machine): Extend the existing safe data/cohort Python package with experiment-domain models, cohort-context loading, file-backed scenario/question/run/response/comparison storage, deterministic mock response execution, repeat-only stability analysis, limited single-step follow-up, and JSONL/CSV exports; no UI and no real API calls.

## Scope

### Goal

- 현재 구현된 `scl-inspect-data`, `scl-profile-categories`, `scl-cohort`를 **그대로 유지**하면서, PRD의 다음 핵심 흐름을 backend/CLI로 완성한다: **코호트 참조 → 시나리오/질문 저장 → mock 반응 실행 → 반복 비교 → 제한된 후속질문 → export**.
- 이 시스템은 여전히 **연구용 synthetic pretest 환경**이며, 실제 시민 여론/수용률/대표성/예측 시스템이 아니다.

### Repository facts to preserve

- 구현된 기능: 안전한 Parquet 점검, 카테고리 프로파일링, 결정론적 cohort 샘플링/저장. References: `README.md`, `src/synthetic_citizen_lab/cli.py`, `src/synthetic_citizen_lab/profile_cli.py`, `src/synthetic_citizen_lab/cohort/`, `tests/test_data_inspector.py`, `tests/test_category_profile.py`, `tests/test_cohort_sampler.py`.
- raw data rules: `data/raw/ko_KR.parquet`는 immutable source data이며, 전체 메모리 적재 금지. References: `AGENTS.md`, `README.md`.
- 검증 명령은 로컬 venv 기준을 따른다: `.venv/bin/ruff check .`, `.venv/bin/python -m pytest`, `.venv/bin/python -c "import synthetic_citizen_lab"`. Reference: `AGENTS.md`, `README.md`.

### Must have

- 기존 `outputs/cohorts/<cohort_id>/cohort.json` artifact를 읽어 실험 입력으로 재사용하는 통합 계층.
- raw Parquet에서 sampled persona ID에 대해 **projection + filter** 방식으로만 P1/P2/P3 context를 읽는 계층.
- 새 실험 도메인 모델: `project`, `scenario`, `question_set`, `run`, `response`, `comparison`, `follow_up`.
- file-backed 저장 구조: JSON metadata + JSONL row records + CSV export.
- 새 CLI surface: `scl-experiment`.
- 시나리오/질문 저장과 불러오기.
- mock response engine과 결정론적 실행기.
- structured response 최소 스키마: `stance`, `stance_score`, `reasoning_summary`, `concerns`, `acceptance_conditions`.
- `ORIGINAL` + `SAME_QUESTION_REPEAT`만 지원하는 반복 안정성 비교.
- 제한된 단일 후속질문 기능.
- overall/cohort/run 단위 비교 요약과 소수 반응 후보 추출.
- CSV/JSONL export.
- TDD 기반 테스트와 기존 회귀 테스트 통과.

### Must NOT have

- Streamlit, Plotly, 브라우저 UI.
- 실제 LLM/API 호출, API key 의존 테스트, `.env` 필수화.
- 기존 cohort sampler 알고리즘/출력 계약의 재설계.
- `PARAPHRASE`, `FRAMING_CHANGE`, `CONTEXT_CHANGE`, 다중 모델 비교.
- 자유형 장기 멀티턴 인터뷰, adaptive branching follow-up.
- NLI, semantic embedding, LLM Judge 기반 자동평가.
- full raw Parquet load, raw data mutation, raw data commit.
- 예측/가중치/추론통계/대표성 claim.

### Concrete implementation locations

- New package area: `src/synthetic_citizen_lab/experiments/`
- New modules to create:
  - `src/synthetic_citizen_lab/experiments/models.py`
  - `src/synthetic_citizen_lab/experiments/storage.py`
  - `src/synthetic_citizen_lab/experiments/context.py`
  - `src/synthetic_citizen_lab/experiments/scenario.py`
  - `src/synthetic_citizen_lab/experiments/questions.py`
  - `src/synthetic_citizen_lab/experiments/engines.py`
  - `src/synthetic_citizen_lab/experiments/runner.py`
  - `src/synthetic_citizen_lab/experiments/analysis.py`
  - `src/synthetic_citizen_lab/experiments/follow_up.py`
  - `src/synthetic_citizen_lab/experiments/export.py`
  - `src/synthetic_citizen_lab/experiment_cli.py`
- Update `pyproject.toml` to register `scl-experiment = "synthetic_citizen_lab.experiment_cli:main"`.
- New tests:
  - `tests/test_experiment_models.py`
  - `tests/test_experiment_storage.py`
  - `tests/test_persona_context.py`
  - `tests/test_experiment_cli.py`
  - `tests/test_mock_engine.py`
  - `tests/test_experiment_runner.py`
  - `tests/test_analysis.py`
  - `tests/test_follow_up.py`
  - `tests/test_export.py`

### Canonical artifact layout

- `outputs/experiments/<project_id>/project.json`
- `outputs/experiments/<project_id>/scenarios/<scenario_id>.json`
- `outputs/experiments/<project_id>/question_sets/<question_set_id>.json`
- `outputs/experiments/<project_id>/runs/<run_id>/run.json`
- `outputs/experiments/<project_id>/runs/<run_id>/responses.jsonl`
- `outputs/experiments/<project_id>/runs/<run_id>/comparisons/repeat_stability.json`
- `outputs/experiments/<project_id>/runs/<run_id>/follow_ups/<follow_up_id>.json`
- `outputs/experiments/<project_id>/exports/<export_name>.jsonl`
- `outputs/experiments/<project_id>/exports/<export_name>.csv`

### Locked behavioral defaults

- Storage backend: local file artifacts only; no DB for this MVP.
- Repeat scope: exactly one repeat after the original question (`repeat_index` values `0` and `1`).
- Question types supported in this plan: `ORIGINAL`, `SAME_QUESTION_REPEAT`, `FOLLOW_UP_LIMITED`.
- Minority-response candidate rule: build a deterministic signature from `(stance, sorted(concerns), sorted(acceptance_conditions))`; any signature frequency `<= 1` within the comparison slice is a minority candidate.
- Follow-up scope: exactly one parent response + one researcher-supplied follow-up question + one resulting follow-up response; no chaining.

## Verification strategy

- Test strategy: **TDD for every new domain rule/module**. For each new module, write failing tests first, then implement, then rerun the full suite.
- Baseline verification commands after every todo:
  - `.venv/bin/ruff check .`
  - `.venv/bin/python -m pytest`
  - `.venv/bin/python -c "import synthetic_citizen_lab"`
- Existing regression commands that must keep passing:
  - `.venv/bin/python -m pytest tests/test_data_inspector.py`
  - `.venv/bin/python -m pytest tests/test_category_profile.py`
  - `.venv/bin/python -m pytest tests/test_cohort_sampler.py`
- Raw-data safety verification after any todo touching experiment execution:
  - Search source for forbidden eager-load patterns against `data/raw/ko_KR.parquet`.
  - Confirm all context reads use projection/filter/sample limits only.
- CLI smoke verification after CLI todo completion:
  - `.venv/bin/scl-experiment --help`
  - fixture-backed `scl-experiment` subcommands for init/save/run/compare/export/follow-up.
- Evidence path per todo:
  - `.omo/evidence/synthetic-citizen-mvp/todo-<N>-<slug>.md`

## Execution strategy

### Execution waves

- Wave 1: integrate experiments with existing cohort artifacts and safe persona context loading.
- Wave 2: define experiment-domain models and file storage contract.
- Wave 3: add scenario/question CLI and persistence.
- Wave 4: add mock engine and run execution.
- Wave 5: add analysis, repeat stability, and limited follow-up.
- Wave 6: add export/report surfaces and doc/CLI contract updates.

### Dependency matrix

| Todo | Depends on | Blocks | Can parallelize with |
| --- | --- | --- | --- |
| 1 Existing cohort integration + context loading | existing repo only | 2, 4, 5 | none |
| 2 Experiment models + storage | 1 | 3, 4, 5, 6 | none |
| 3 Scenario/question CLI | 2 | 4, 5, 6 | none |
| 4 Mock engine + runner | 1, 2, 3 | 5, 6 | none |
| 5 Analysis + repeat + follow-up | 1, 2, 3, 4 | 6 | none |
| 6 Export + docs/contract polish | 2, 3, 4, 5 | Final verification | none |

### Worker discipline

- Do not redesign `src/synthetic_citizen_lab/cohort/` unless a failing regression test proves a bug.
- Prefer adding thin integration helpers around existing cohort artifacts over moving their location or schema.
- Keep each new module under ~250 LOC if possible; split helpers early rather than building one giant runner.
- Use fixture Parquet tables in tests; do not use the real raw file as a test fixture.

## Todos

> Implementation + Test = ONE todo. Never separate.
<!-- APPEND TASK BATCHES BELOW THIS LINE WITH edit/apply_patch - never rewrite the headers above. -->

- [ ] 1. Preserve existing cohort contracts and add safe persona-context loading
  What to do / Must NOT do: Add `src/synthetic_citizen_lab/experiments/context.py` that loads existing cohort definitions via `cohort.json`, reads sampled persona rows from the source Parquet by `persona_ids`, and returns only whitelisted P1/P2/P3 fields using DuckDB/PyArrow projection + `uuid IN (...)` filtering. Reuse current `cohort/storage.py` and `cohort/models.py`; do not change current sampler output names or deterministic behavior unless a regression test proves a bug.
  Parallelization: Wave 1 | Blocked by: existing repo only | Blocks: Todos 2, 4, 5
  References (executor has NO interview context - be exhaustive): `README.md`; `AGENTS.md`; `src/synthetic_citizen_lab/cohort/models.py`; `src/synthetic_citizen_lab/cohort/sampler.py`; `src/synthetic_citizen_lab/cohort/storage.py`; `docs/cohort_sampler.md`; `tests/test_cohort_sampler.py`; PRD P1/P2/P3 context expectations from `docs/PRD.md` and `docs/PRD_APPENDIX.md`.
  Acceptance criteria (agent-executable): existing cohort tests still pass unchanged; new context loader can consume a fixture cohort artifact and return P1-only, P2-only, and P3 rows with correct field inclusion/exclusion; loader rejects missing cohort paths and missing source files clearly; no new code path loads the full raw Parquet into memory.
  QA scenarios (exact tool + invocation): happy: `.venv/bin/python -m pytest tests/test_cohort_sampler.py tests/test_persona_context.py`; failure: run a test case with a missing `cohort.json` and assert explicit error text. Evidence: `.omo/evidence/synthetic-citizen-mvp/todo-1-context.md`.
  Commit: Y when user requests commits | `feat(experiments): add cohort-backed persona context loader`

- [ ] 2. Define experiment-domain schemas and file storage contract
  What to do / Must NOT do: Create `experiments/models.py` and `experiments/storage.py` with Pydantic models and read/write helpers for `ProjectRecord`, `ScenarioRecord`, `QuestionSetRecord`, `RunRecord`, `ResponseRecord`, `ComparisonRecord`, and `FollowUpRecord`. Encode IDs and references explicitly: `project_id`, `cohort_id`, `scenario_id`, `question_id`, `run_id`, `response_id`, `comparison_id`, `follow_up_id`. Persist only under `outputs/experiments/<project_id>/...`; do not introduce SQLite/Parquet/DB storage in this MVP.
  Parallelization: Wave 2 | Blocked by: Todo 1 | Blocks: Todos 3, 4, 5, 6
  References (executor has NO interview context - be exhaustive): `docs/PRD.md` sections FR-02 through FR-06; `docs/PRD_APPENDIX.md` sections 4.1-4.4; current file-artifact conventions in `src/synthetic_citizen_lab/cohort/storage.py`; existing typed models in `src/synthetic_citizen_lab/data/models.py` and `src/synthetic_citizen_lab/cohort/models.py`.
  Acceptance criteria (agent-executable): model validation covers required IDs, enums, repeat indices, and minimal structured response schema; storage helpers create the canonical artifact layout exactly; invalid cross-references fail validation; record serialization is deterministic enough for stable fixture assertions.
  QA scenarios (exact tool + invocation): happy: `.venv/bin/python -m pytest tests/test_experiment_models.py tests/test_experiment_storage.py`; failure: create a response record with a missing `run_id` or invalid `question_type` and assert validation failure. Evidence: `.omo/evidence/synthetic-citizen-mvp/todo-2-models-storage.md`.
  Commit: Y when user requests commits | `feat(experiments): add experiment records and storage contract`

- [ ] 3. Add `scl-experiment` CLI for project, scenario, and question-set management
  What to do / Must NOT do: Add `src/synthetic_citizen_lab/experiment_cli.py` and register `scl-experiment` in `pyproject.toml`. Implement minimal subcommands: `init-project`, `save-scenario`, `save-questions`, and `show`. Each command must read/write the canonical file artifacts from Todo 2. `save-questions` must only support `ORIGINAL` plus repeat metadata for `SAME_QUESTION_REPEAT`; do not add `PARAPHRASE` or collaborative editing workflows.
  Parallelization: Wave 3 | Blocked by: Todo 2 | Blocks: Todos 4, 5, 6
  References (executor has NO interview context - be exhaustive): `pyproject.toml`; CLI style from `src/synthetic_citizen_lab/cli.py`, `profile_cli.py`, `cohort_cli.py`; PRD FR-02 in `docs/PRD.md`; repeat-question constraints in `docs/PRD_APPENDIX.md` section 1.
  Acceptance criteria (agent-executable): `scl-experiment --help` works; fixture-backed CLI tests can initialize a project, save one scenario with A/B/C variants, save one question set with one original question and repeat metadata, and read the saved records back; unsupported question types fail with explicit usage errors.
  QA scenarios (exact tool + invocation): happy: `.venv/bin/python -m pytest tests/test_experiment_cli.py -k "project or scenario or question"`; failure: invoke `save-questions` with `PARAPHRASE` in fixture input and assert rejection. Evidence: `.omo/evidence/synthetic-citizen-mvp/todo-3-cli.md`.
  Commit: Y when user requests commits | `feat(cli): add experiment project and question management`

- [ ] 4. Implement deterministic mock response engine and experiment runner
  What to do / Must NOT do: Add `experiments/engines.py` and `experiments/runner.py`. Implement a `ResponseEngine` protocol/interface and a deterministic `MockResponseEngine` that produces stable structured responses from the tuple `(persona_id, scenario_id, question_id, seed, repeat_index)`. Runner must consume one or more existing cohort dirs, scenario/question artifacts, and context loader outputs, then write `run.json` and `responses.jsonl`. Add a placeholder disabled live-engine config object only if needed for type completeness, but do not make network calls or require API keys.
  Parallelization: Wave 4 | Blocked by: Todos 1, 2, 3 | Blocks: Todos 5, 6
  References (executor has NO interview context - be exhaustive): PRD FR-03 in `docs/PRD.md`; structured response example in `docs/PRD_APPENDIX.md` section 4.2; current no-API-key rule in `AGENTS.md`; existing reproducibility patterns in `src/synthetic_citizen_lab/cohort/sampler.py` and `tests/test_cohort_sampler.py`.
  Acceptance criteria (agent-executable): same inputs produce byte-stable or field-stable mock responses across reruns; runner writes one response per `(persona_id, question_id, repeat_index)` combination; `repeat_index` values are exactly `0` and `1`; failed engine execution is recorded as an error response record without aborting the whole run; no environment variable is required for tests.
  QA scenarios (exact tool + invocation): happy: `.venv/bin/python -m pytest tests/test_mock_engine.py tests/test_experiment_runner.py`; failure: run a fixture where the mock engine is instructed to fail for one persona and assert the runner stores an error record and continues. Evidence: `.omo/evidence/synthetic-citizen-mvp/todo-4-runner.md`.
  Commit: Y when user requests commits | `feat(experiments): add deterministic mock runner`

- [ ] 5. Add repeat-stability analysis, minority-response detection, and limited follow-up
  What to do / Must NOT do: Add `experiments/analysis.py` and `experiments/follow_up.py`. Implement comparison generation only for `ORIGINAL` ↔ `SAME_QUESTION_REPEAT` pairs. Compute `stance_match`, `stance_score_delta`, `concern_overlap`, `acceptance_condition_overlap`, `contradiction_candidate`, and `needs_human_review`; emit `ComparisonRecord` to `comparisons/repeat_stability.json`. Implement minority-response candidate extraction using the locked signature rule. Implement one limited follow-up path storing `parent_response_id`, follow-up question text, and exactly one follow-up response artifact. Do not add paraphrase, multi-turn chains, NLI, embeddings, or LLM Judge.
  Parallelization: Wave 5 | Blocked by: Todos 1, 2, 3, 4 | Blocks: Todo 6
  References (executor has NO interview context - be exhaustive): PRD FR-04 through FR-06 in `docs/PRD.md`; repeat/evaluation constraints in `docs/PRD_APPENDIX.md` sections 1 and 2; approved defaults in this plan Scope.
  Acceptance criteria (agent-executable): comparison output contains one record per original-repeat pair; metrics are deterministic on fixture data; minority candidate extraction returns the expected low-frequency signatures; limited follow-up creates exactly one linked follow-up artifact and refuses chained follow-up on a follow-up response.
  QA scenarios (exact tool + invocation): happy: `.venv/bin/python -m pytest tests/test_analysis.py tests/test_follow_up.py`; failure: attempt a second chained follow-up from an existing follow-up response and assert explicit rejection. Evidence: `.omo/evidence/synthetic-citizen-mvp/todo-5-analysis-followup.md`.
  Commit: Y when user requests commits | `feat(experiments): add repeat comparison and limited follow-up`

- [ ] 6. Add export workflow and align docs/CLI contracts
  What to do / Must NOT do: Add `experiments/export.py` and finish `scl-experiment` subcommands `run`, `compare`, `follow-up`, and `export`. Export at minimum `responses.jsonl` passthrough and one CSV summary with deterministic row ordering. Update `README.md` and any relevant docs to reflect the real backend/CLI-first MVP boundaries and non-claim text. Do not add Streamlit, browser flows, or API setup instructions.
  Parallelization: Wave 6 | Blocked by: Todos 2, 3, 4, 5 | Blocks: Final verification
  References (executor has NO interview context - be exhaustive): `README.md`; `AGENTS.md`; PRD export requirements in `docs/PRD.md`; current CLI conventions; canonical artifact layout in this plan.
  Acceptance criteria (agent-executable): fixture-backed `scl-experiment run`, `compare`, `follow-up`, and `export` succeed end-to-end; export writes both JSONL and CSV under `outputs/experiments/<project_id>/exports/`; README/docs clearly state no UI, no real API calls, and non-predictive research scope; full test suite and Ruff pass.
  QA scenarios (exact tool + invocation): happy: `.venv/bin/python -m pytest tests/test_export.py tests/test_experiment_cli.py -k "run or compare or follow_up or export" && .venv/bin/ruff check . && .venv/bin/python -m pytest`; failure: request export for a nonexistent `run_id` and assert a clear CLI error. Evidence: `.omo/evidence/synthetic-citizen-mvp/todo-6-export.md`.
  Commit: Y when user requests commits | `feat(experiments): add cli export workflow`

## Final verification wave

> Runs in parallel after ALL todos. ALL must APPROVE. Surface results and wait for the user's explicit okay before declaring complete.

- [ ] F1. Plan compliance audit
  - Verify every Must have in this plan is implemented.
  - Verify every Must NOT have remains absent, especially Streamlit, real API calls, paraphrase support, and new sampler algorithms.
  - Evidence: `.omo/evidence/synthetic-citizen-mvp/final-plan-compliance.md`.

- [ ] F2. Code quality and regression audit
  - Run `.venv/bin/ruff check .`.
  - Run `.venv/bin/python -m pytest`.
  - Re-run focused regressions for existing implemented areas: `tests/test_data_inspector.py`, `tests/test_category_profile.py`, `tests/test_cohort_sampler.py`.
  - Evidence: `.omo/evidence/synthetic-citizen-mvp/final-code-quality.md`.

- [ ] F3. Agent-executed end-to-end CLI QA
  - Using fixture data and a fixture cohort artifact, run the CLI flow: `init-project` → `save-scenario` → `save-questions` → `run` → `compare` → `follow-up` → `export`.
  - Verify expected files exist under `outputs/experiments/<project_id>/...` and that summary CSV row counts match response/comparison artifacts.
  - Evidence: `.omo/evidence/synthetic-citizen-mvp/final-cli-qa.md`.

- [ ] F4. Raw-data safety and scope-fidelity audit
  - Search for forbidden raw-file eager-load patterns.
  - Confirm no writes occurred under `data/raw/`.
  - Confirm docs and CLI text preserve the non-claim language.
  - Evidence: `.omo/evidence/synthetic-citizen-mvp/final-safety-scope.md`.

## Commit strategy

- This planning request does not authorize commits.
- If implementation later happens, prefer one commit per todo only when the todo is independently reviewable and tested.
- Never commit `data/raw/ko_KR.parquet`, generated experiment artifacts, `.env`, or `.omo/evidence` unless explicitly requested.
- Before any commit, inspect `git status`, `git diff`, and `git log --oneline -10`.

## Success criteria

- Existing inspection/profile/cohort functionality still works unchanged from the user’s perspective.
- A worker can create a project, save a scenario, save questions, run a deterministic mock experiment from an existing cohort artifact, compare original vs repeat responses, record one limited follow-up, and export JSONL/CSV entirely through CLI/file workflows.
- Every stored response is linked to `project_id`, `cohort_id`, `scenario_id`, `question_id`, `run_id`, and `repeat_index`.
- Repeat support is limited to `ORIGINAL` and `SAME_QUESTION_REPEAT`, with exactly one repeat.
- No real API keys are needed; tests pass in a clean local environment.
- No code path fully loads or mutates the raw Parquet file.
- README/docs accurately describe the implemented MVP as a backend/CLI-first synthetic-research tool, not a public-opinion predictor.
