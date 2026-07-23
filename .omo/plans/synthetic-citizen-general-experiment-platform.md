# synthetic-citizen-general-experiment-platform - Work Plan

## TL;DR (For humans)

**What you'll get:** 기존의 좁은 “반복 비교 + follow-up + export” 5단계를, 질문 변형·페르소나 정보량·모델 조건·평가 지표를 조합할 수 있는 범용 실험 플랫폼 계획으로 바꾼다. H1/H2/H3는 시스템에 박힌 전용 기능이 아니라 설정 가능한 분석 preset으로만 둔다.

**Why this approach:** 지금 구현된 CLI/mock runner는 좋은 기반이지만, 바로 H1/H2/H3 전용 분석을 만들면 이후 실험이 막힌다. 먼저 실험 설계, 조건 행렬, 평가 지표 계약, 분석 recipe를 분리해야 PRD_APPENDIX의 다양한 질문 변형을 확장 가능하게 담을 수 있다.

**What it will NOT do:** 이 계획은 Streamlit UI, 실제 LLM/API 호출, 장기 자유형 인터뷰, 고급 NLI/embedding/Judge 실제 구현을 포함하지 않는다. raw Parquet 안전 제약과 비예측 연구도구 원칙은 그대로 유지한다.

**Effort:** XL
**Risk:** Medium - 현재 단일 mock run 구조를 조건 행렬/평가/recipe 구조로 확장해야 하므로 schema 경계가 가장 중요하다.
**Decisions to sanity-check:** JSON 기반 설계/recipe 파일, mock-only model condition, H1/H2/H3 preset-only 원칙, advanced metric은 계약만 먼저 정의.

Your next move: 이 계획대로 구현하려면 `$start-work`를 요청한다. 실행 전 더 엄격한 계획 리뷰를 원하면 `review first`라고 말하면 된다. Full execution detail follows below.

---

> TL;DR (machine): XL/Medium; revise phase 5+ into a general experiment-design, condition-matrix, metric-registry, recipe, human-packet, and tidy-export platform without UI, real LLM calls, or H1/H2/H3 hardcoding.

## Scope

### Must have

- Preserve current phase 1-4 implementation: context loader, experiment records/storage, `scl-experiment` metadata CLI, deterministic mock `run` writing `run.json` and `responses.jsonl`.
- Add a general experiment design layer that can represent the seven PRD_APPENDIX condition/question variant types: `ORIGINAL`, `SAME_QUESTION_REPEAT`, `PARAPHRASE`, `FRAMING_CHANGE`, `CONTEXT_CHANGE`, `SOCIAL_PRESSURE`, and `MODEL_CONDITION_CHANGE`.
- Add explicit condition metadata rather than relying on a flat question enum alone:
  - original base question reference.
  - repeat source question and repeat index.
  - paraphrase source and invariant fields.
  - framing direction/label and framing text.
  - context-change payload/source.
  - social-pressure source, pressure level, and pressure text.
  - model-condition label/config metadata, mock-compatible only.
- Add design validation so malformed/incomplete condition definitions fail before execution.
- Add a condition matrix compiler that expands experiment designs into executable condition cells across question variant, persona context level, scenario variant, and model condition.
- Add a condition-aware runner that consumes compiled condition cells and existing cohort/scenario/question artifacts without full raw Parquet loads.
- Add a metric registry with name, version, required inputs, output schema, status, and deterministic evaluator contract.
- Implement deterministic/rule-based MVP metrics: stance consistency, stance score delta, concern/reason overlap, acceptance-condition overlap, contradiction candidate, profile-consistency candidate, reason specificity heuristic, defensiveness heuristic, stance clarity, persona attribute usage, minority-response candidate flag, human-review-needed flag.
- Represent semantic similarity, NLI contradiction, and LLM Judge metrics as explicit `not_computed`/`unsupported_without_model` records until actual LLM/embedding scope is approved.
- Add analysis recipes that express H1/H2/H3 as presets only; core schema, runner, storage, and metrics must not mention H1/H2/H3.
- Add at least one non-H1/H2/H3 recipe fixture proving the platform is not hypothesis-hardcoded.
- Add limited follow-up as a recipe-triggered, one-step artifact linked to a parent response; no free-form multi-turn chat.
- Add human evaluation packet generation as file artifacts, not UI.
- Add tidy exports for design, condition matrix, responses, comparisons, metrics, recipe summaries, human-review samples, and provenance.
- Update docs to explain the changed phase-5+ roadmap, including the difference from the original PRD plan.

### Must NOT have (guardrails, anti-slop, scope boundaries)

- No Streamlit, Plotly dashboard, browser UI, web app, background worker service, or manual visual QA.
- No real LLM/API calls, provider SDK setup, network calls, `.env` dependency, or API-key-required tests.
- No mutation, move, resave, staging, or commit of `data/raw/ko_KR.parquet`; no full raw Parquet memory loads.
- No public-opinion prediction, representativeness, actual-citizen equivalence, or automated real-world decision claims.
- No H1/H2/H3-specific core models, runner branches, storage paths, metric functions, or CLI commands such as `run-h1`.
- No arbitrary plugin condition system in this plan; implement the PRD_APPENDIX built-ins plus metadata extension fields only.
- No free-form long multi-turn interview or agent debate/social-spread simulation.
- No fake advanced metric values; unsupported advanced metrics must be recorded as not computed.

## Verification strategy

> Zero human intervention - all verification is agent-executed.

- Test decision: TDD for new domain rules and tests-after for documentation-only updates; framework is pytest plus repo Ruff command.
- Required commands after implementation todos:
  - `.venv/bin/ruff check .`
  - `.venv/bin/python -m pytest`
  - `.venv/bin/python -c "import synthetic_citizen_lab"`
- Focused regression commands:
  - `.venv/bin/python -m pytest tests/test_experiment_models.py tests/test_experiment_storage.py tests/test_experiment_runner.py tests/test_experiment_run_cli.py`
  - `.venv/bin/python -m pytest tests/test_persona_context.py tests/test_cohort_sampler.py`
- Manual QA gate for CLI/file artifact work:
  - Run a fixture-backed CLI flow through `scl-experiment` design creation, matrix compilation, matrix run, metric evaluation, recipe summary, human-packet export, and tidy export.
  - Try one invalid condition definition and verify a clear CLI/test error.
- Evidence paths: `.omo/evidence/synthetic-citizen-general-experiment-platform/todo-<N>-<slug>.md`.

## Execution strategy

### Parallel execution waves

- Wave 5A: introduce experiment design and condition variant schema.
- Wave 5B: add condition matrix compiler and condition-aware mock runner integration.
- Wave 5C: add metric registry and deterministic evaluator outputs.
- Wave 5D: add analysis recipes, H1/H2/H3 presets, non-hypothesis recipe, limited follow-up selectors, and minority selectors.
- Wave 5E: add human evaluation packet and tidy exports.
- Wave 5F: update docs/CLI contract and run final verification.

### Dependency matrix

| Todo | Depends on | Blocks | Can parallelize with |
| --- | --- | --- | --- |
| 1 Design schema | current phase 4 code | 2, 3, 4, 5, 6, 7 | none |
| 2 Design storage + CLI | 1 | 3, 4, 5, 6, 7 | none |
| 3 Condition matrix compiler | 1, 2 | 4, 5, 6, 7 | none |
| 4 Condition-aware mock runner | 1, 2, 3 | 5, 6, 7 | none |
| 5 Metric registry/evaluators | 1, 4 | 6, 7 | docs-only drafting after schema stabilizes |
| 6 Analysis recipes/selectors | 1, 3, 4, 5 | 7 | none |
| 7 Human packet + tidy exports + docs | 1-6 | final verification | none |

## Todos

> Implementation + Test = ONE todo. Never separate.
<!-- APPEND TASK BATCHES BELOW THIS LINE WITH edit/apply_patch - never rewrite the headers above. -->

- [ ] 1. Add general experiment design and condition variant models
  What to do / Must NOT do: Add `src/synthetic_citizen_lab/experiments/design.py` and, if needed, `src/synthetic_citizen_lab/experiments/conditions.py`. Define `ExperimentDesignRecord`, condition IDs, `QuestionVariantCondition`, `PersonaContextCondition`, `ModelCondition`, `MetricSpec`, and design-level provenance. Extend or wrap current `QuestionType` without breaking existing `ORIGINAL`/`SAME_QUESTION_REPEAT` records. Encode required metadata for all seven PRD_APPENDIX condition types. Do not add H1/H2/H3 fields or real provider configuration secrets.
  Parallelization: Wave 5A | Blocked by: current phase 4 code | Blocks: Todos 2-7
  References (executor has NO interview context - be exhaustive): `AGENTS.md:1-12`; `docs/PRD.md:276-292`; `docs/PRD.md:390-400`; `docs/PRD_APPENDIX.md:9-79`; `docs/PRD_APPENDIX.md:190-277`; `src/synthetic_citizen_lab/experiments/model_types.py:31-65`; `src/synthetic_citizen_lab/experiments/models.py:61-147`.
  Acceptance criteria (agent-executable): pytest proves all seven condition/question variant types are representable; invalid missing fields fail validation; design serialization round-trips deterministically; a fixture non-H1 design validates.
  QA scenarios (name the exact tool + invocation): happy: `.venv/bin/python -m pytest tests/test_experiment_design.py tests/test_condition_variants.py`; failure: create `SOCIAL_PRESSURE` without pressure text and assert validation failure. Evidence `.omo/evidence/synthetic-citizen-general-experiment-platform/todo-1-design.md`.
  Commit: Y when user requests commits | `feat(experiments): add general experiment design schema`

- [ ] 2. Add design storage and CLI commands without disturbing existing metadata/run commands
  What to do / Must NOT do: Add storage helpers for `outputs/experiments/<project_id>/designs/<design_id>.json` and CLI parsing/actions for `scl-experiment save-design` and `show design`. Keep existing `init-project`, `save-scenario`, `save-questions`, `show`, and `run` behavior compatible. Use JSON input for design payloads; do not add YAML or a new dependency unless the repo already has it.
  Parallelization: Wave 5A | Blocked by: Todo 1 | Blocks: Todos 3-7
  References (executor has NO interview context - be exhaustive): `src/synthetic_citizen_lab/experiments/storage.py:27-149`; `src/synthetic_citizen_lab/experiment_cli.py:26-116`; `src/synthetic_citizen_lab/_experiment_cli_args.py:83-229`; `src/synthetic_citizen_lab/_experiment_cli_actions.py:50-202`; `docs/experiment_cli.md:1-79`.
  Acceptance criteria (agent-executable): CLI can save/show a design JSON fixture; path traversal IDs are rejected; existing phase-3/4 CLI tests still pass; `save-design` rejects H1/H2/H3-only special command shapes.
  QA scenarios (name the exact tool + invocation): happy: `.venv/bin/python -m pytest tests/test_experiment_design_cli.py tests/test_experiment_cli.py tests/test_experiment_run_cli.py`; failure: `save-design` with `--project-id ../outside` returns a clear error. Evidence `.omo/evidence/synthetic-citizen-general-experiment-platform/todo-2-design-cli.md`.
  Commit: Y when user requests commits | `feat(cli): add experiment design artifacts`

- [ ] 3. Compile experiment designs into deterministic condition matrices
  What to do / Must NOT do: Add `src/synthetic_citizen_lab/experiments/matrix.py`. Compile each design into condition cells with stable `condition_id`, `design_id`, `scenario_id`, `question_id` or generated variant reference, `question_variant_type`, `persona_context_level`, `model_condition_id`, and provenance. Ensure deterministic ordering and bounded expected response counts. Do not execute responses in the compiler.
  Parallelization: Wave 5B | Blocked by: Todos 1, 2 | Blocks: Todos 4, 5, 6, 7
  References (executor has NO interview context - be exhaustive): `docs/PRD_APPENDIX.md:9-79`; `docs/PRD_APPENDIX.md:265-277`; `src/synthetic_citizen_lab/experiments/runner.py:36-127`; `src/synthetic_citizen_lab/experiments/context_models.py`; `tests/test_experiment_runner.py`.
  Acceptance criteria (agent-executable): matrix compilation expands a fixture across question variants × P1/P2/P3 × model conditions with stable IDs; duplicate or impossible cells fail validation; expected response count is reported without touching raw data.
  QA scenarios (name the exact tool + invocation): happy: `.venv/bin/python -m pytest tests/test_condition_matrix.py`; failure: duplicate condition ID input raises a deterministic error. Evidence `.omo/evidence/synthetic-citizen-general-experiment-platform/todo-3-matrix.md`.
  Commit: Y when user requests commits | `feat(experiments): compile condition matrices`

- [ ] 4. Extend mock execution to run condition matrices safely
  What to do / Must NOT do: Add a matrix-run request/runner or extend `runner.py` with a separate `run_condition_matrix` function. Write artifacts under `outputs/experiments/<project_id>/runs/<run_id>/condition_matrix.json` and condition-scoped responses while preserving current `run.json`/`responses.jsonl` compatibility. Mock engine may use model-condition metadata deterministically but must not call networks or read `.env`. Persona context loading must remain bounded to sampled cohort IDs and requested P-level fields.
  Parallelization: Wave 5B | Blocked by: Todos 1, 2, 3 | Blocks: Todos 5, 6, 7
  References (executor has NO interview context - be exhaustive): `AGENTS.md:8-11`; `src/synthetic_citizen_lab/experiments/context.py`; `src/synthetic_citizen_lab/experiments/engines.py:37-110`; `src/synthetic_citizen_lab/experiments/runner.py:69-216`; `docs/PRD.md:276-292`; `docs/PRD_APPENDIX.md:207-235`.
  Acceptance criteria (agent-executable): fixture matrix run writes one response per persona × condition cell; `MODEL_CONDITION_CHANGE` is captured as metadata; no API keys are read; no full raw Parquet load patterns are introduced; existing `run` tests still pass.
  QA scenarios (name the exact tool + invocation): happy: `.venv/bin/python -m pytest tests/test_condition_matrix_runner.py tests/test_experiment_runner.py tests/test_experiment_run_cli.py`; failure: configure a mock failure for one persona/cell and assert error response is stored while the run continues. Evidence `.omo/evidence/synthetic-citizen-general-experiment-platform/todo-4-matrix-runner.md`.
  Commit: Y when user requests commits | `feat(experiments): run condition matrices with mock engine`

- [ ] 5. Add metric registry and deterministic evaluator records
  What to do / Must NOT do: Add `src/synthetic_citizen_lab/experiments/metrics.py` and `src/synthetic_citizen_lab/experiments/evaluation.py`. Define metric specs/results with `metric_name`, `metric_version`, `required_inputs`, `status`, `value`, `details`, and `needs_human_review`. Implement deterministic MVP metrics only. Record semantic similarity, NLI, and LLM Judge metrics as not computed when requested without provider support; do not invent values.
  Parallelization: Wave 5C | Blocked by: Todos 1, 4 | Blocks: Todos 6, 7
  References (executor has NO interview context - be exhaustive): `docs/PRD.md:329-345`; `docs/PRD.md:362-372`; `docs/PRD_APPENDIX.md:81-130`; `docs/PRD_APPENDIX.md:238-263`; `src/synthetic_citizen_lab/experiments/models.py:148-244`.
  Acceptance criteria (agent-executable): registry lists supported and unsupported metrics; deterministic metrics compute expected fixture values; missing required inputs produce not-computed records; unsupported advanced metrics do not fail the whole evaluation.
  QA scenarios (name the exact tool + invocation): happy: `.venv/bin/python -m pytest tests/test_metric_registry.py tests/test_experiment_evaluation.py`; failure: request `semantic_similarity` without embedding provider and assert `status=not_computed`. Evidence `.omo/evidence/synthetic-citizen-general-experiment-platform/todo-5-metrics.md`.
  Commit: Y when user requests commits | `feat(experiments): add metric registry and evaluators`

- [ ] 6. Add analysis recipes, H presets, minority selectors, and limited follow-up selectors
  What to do / Must NOT do: Add `src/synthetic_citizen_lab/experiments/recipes.py`, `selectors.py`, and follow-up integration if not already adequate. Encode recipes as JSON artifacts under `outputs/experiments/<project_id>/recipes/<recipe_id>.json` or package fixtures. Provide preset fixtures for H1 question variation, H2 persona context level, H3 model-condition interaction, plus one non-H recipe. Recipes define group-by fields, comparison baselines, selected metrics, filters, minority selector, and optional limited follow-up selector. Do not create `run_h1`, `run_h2`, or `run_h3` APIs.
  Parallelization: Wave 5D | Blocked by: Todos 1, 3, 4, 5 | Blocks: Todo 7
  References (executor has NO interview context - be exhaustive): checkpoint summary of user-provided H1/H2/H3; `docs/PRD.md:92-110`; `docs/PRD.md:312-327`; `docs/PRD_APPENDIX.md:133-186`; `docs/PRD_APPENDIX.md:238-263`; `.omo/drafts/synthetic-citizen-general-experiment-platform.md:42-49`.
  Acceptance criteria (agent-executable): H1/H2/H3 recipe fixtures validate; non-H recipe validates and runs through summary generation; static search or tests prove no core module contains H-specific branches; limited follow-up selector creates max one follow-up per selected parent response and rejects chained free-form chat.
  QA scenarios (name the exact tool + invocation): happy: `.venv/bin/python -m pytest tests/test_analysis_recipes.py tests/test_minority_selectors.py tests/test_follow_up.py`; failure: recipe referencing a nonexistent metric fails validation before execution. Evidence `.omo/evidence/synthetic-citizen-general-experiment-platform/todo-6-recipes.md`.
  Commit: Y when user requests commits | `feat(experiments): add analysis recipes and selectors`

- [ ] 7. Add human-evaluation packets, tidy exports, docs, and CLI contract polish
  What to do / Must NOT do: Add `src/synthetic_citizen_lab/experiments/human_eval.py` and extend/export module(s) for tidy outputs. Emit CSV/JSONL artifacts for condition matrix, responses long, comparisons long, metric results long, recipe summaries, minority candidates, and human-evaluation samples/instructions. Include provenance fields: project/design/run/condition IDs, metric versions, prompt/model metadata, context level, and export schema version. Update `docs/experiment_cli.md`, `README.md` if needed, and add/maintain the revised roadmap document in `docs/`. Do not add UI or require a human to complete verification.
  Parallelization: Wave 5E/5F | Blocked by: Todos 1-6 | Blocks: Final verification
  References (executor has NO interview context - be exhaustive): `docs/PRD.md:329-345`; `docs/PRD_APPENDIX.md:133-186`; `docs/PRD_APPENDIX.md:330-339`; `README.md`; `docs/experiment_cli.md:71-79`; `AGENTS.md:1-12`.
  Acceptance criteria (agent-executable): CLI or library export writes deterministic CSV/JSONL with expected columns; human-eval packet excludes excessive raw profile fields and includes reviewer instructions; docs describe old-vs-new phase-5+ plan and current no-UI/no-LLM boundaries; full repo verification passes.
  QA scenarios (name the exact tool + invocation): happy: `.venv/bin/python -m pytest tests/test_human_eval_packets.py tests/test_tidy_exports.py tests/test_experiment_cli.py && .venv/bin/ruff check . && .venv/bin/python -m pytest && .venv/bin/python -c "import synthetic_citizen_lab"`; failure: export nonexistent `run_id` and assert clear error. Evidence `.omo/evidence/synthetic-citizen-general-experiment-platform/todo-7-export-docs.md`.
  Commit: Y when user requests commits | `feat(experiments): add human review packets and tidy exports`

## Final verification wave

> Runs in parallel after ALL todos. ALL must APPROVE. Surface results and wait for the user's explicit okay before declaring complete.

- [ ] F1. Plan compliance audit
  - Verify all Must have items exist.
  - Verify all Must NOT items remain absent, especially real LLM/API calls, UI, H1/H2/H3 core hardcoding, and raw Parquet mutation/full loads.
  - Evidence: `.omo/evidence/synthetic-citizen-general-experiment-platform/final-plan-compliance.md`.

- [ ] F2. Code quality review
  - Run `.venv/bin/ruff check .`.
  - Run `.venv/bin/python -m pytest`.
  - Run `.venv/bin/python -c "import synthetic_citizen_lab"`.
  - Evidence: `.omo/evidence/synthetic-citizen-general-experiment-platform/final-code-quality.md`.

- [ ] F3. Real CLI/manual QA
  - Use fixture artifacts to run `scl-experiment` through project/scenario/question/design creation, condition matrix compilation, matrix run, metric evaluation, recipe summary, human-packet generation, and tidy export.
  - Try one invalid design and one nonexistent export target; verify clear errors.
  - Evidence: `.omo/evidence/synthetic-citizen-general-experiment-platform/final-cli-qa.md`.

- [ ] F4. Scope fidelity
  - Inspect changed files for no UI/API/provider setup and no `.env` dependence.
  - Confirm docs preserve non-predictive synthetic-research framing.
  - Confirm `data/raw/ko_KR.parquet` was not modified, moved, staged, or read eagerly.
  - Evidence: `.omo/evidence/synthetic-citizen-general-experiment-platform/final-scope-fidelity.md`.

## Commit strategy

- This planning/documentation request does not authorize commits.
- If implementation later happens, prefer one commit per completed todo only when independently reviewable and verified.
- Never commit raw data, `.env`, generated outputs, or `.omo/evidence` unless explicitly requested.
- Before any commit, inspect `git status`, `git diff`, and `git log --oneline -10`.

## Success criteria

- The downstream worker has a decision-complete phase-5+ plan that requires no extra interview.
- The old repeat/follow-up/export Wave 5 is explicitly replaced by a general experiment-platform sequence.
- H1/H2/H3 are implemented only as recipe fixtures/presets; at least one non-H recipe proves generality.
- All seven PRD_APPENDIX condition/question variant types are representable and validated.
- Condition matrix execution remains mock-only, file-backed, deterministic, and bounded to sampled cohort data.
- Metric registry records supported and unsupported metrics honestly, without fake semantic/NLI/Judge values.
- Human evaluation and exports are reproducible file artifacts, not UI workflows.
- Repo safety and verification constraints from `AGENTS.md` remain satisfied.
