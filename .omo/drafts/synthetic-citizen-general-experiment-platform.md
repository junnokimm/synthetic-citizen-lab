---
slug: synthetic-citizen-general-experiment-platform
status: planned
intent: clear
pending-action: write .omo/plans/synthetic-citizen-general-experiment-platform.md
approach: Replace the original narrow Wave 5 repeat/follow-up/export implementation with a general, mock-only experiment-platform roadmap: design schema, condition matrix, condition-aware runner, metric registry, analysis recipes/presets, human-evaluation packets, and tidy exports. H1/H2/H3 are recipe presets only, never core schema or runner concepts.
---

# Draft: synthetic-citizen-general-experiment-platform

## Components (topology ledger)
<!-- Lock the SHAPE before depth. One row per top-level component that can succeed or fail independently. -->
<!-- id | outcome (one line) | status: active|deferred | evidence path -->
- C1 | Current experiment metadata/run MVP remains stable as the base layer for the revised platform | active | src/synthetic_citizen_lab/experiments/models.py:31-271; src/synthetic_citizen_lab/experiments/runner.py:69-127; docs/experiment_cli.md:1-79
- C2 | General experiment design schema can represent PRD_APPENDIX question variants and condition axes without H1/H2/H3 hardcoding | active | docs/PRD_APPENDIX.md:9-24; docs/PRD_APPENDIX.md:405-415
- C3 | Condition matrix compiler and runner execute combinations of question variant, persona context level, and model condition using mock-compatible metadata | active | docs/PRD.md:276-292; docs/PRD.md:390-400; src/synthetic_citizen_lab/experiments/runner.py:36-127
- C4 | Metric registry evaluates responses/comparisons with deterministic contracts and records unsupported advanced metrics explicitly | active | docs/PRD_APPENDIX.md:81-130; docs/PRD.md:362-372
- C5 | Analysis recipes express H1/H2/H3 and non-hypothesis experiments as configurable grouping/metric/export plans | active | user-provided H1/H2/H3 summary from checkpoint; docs/PRD.md:92-110; docs/PRD_APPENDIX.md:238-263
- C6 | Human evaluation packets, limited follow-up selection, minority candidates, and tidy exports remain CLI/file artifacts, not UI/API features | active | docs/PRD.md:312-345; docs/PRD_APPENDIX.md:133-186; docs/PRD_APPENDIX.md:330-339
- C7 | Actual LLM/API integration, Streamlit UI, arbitrary chat, and advanced NLI/embedding/Judge implementations remain deferred | deferred | AGENTS.md:10-11; docs/PRD.md:173-183; docs/PRD_APPENDIX.md:120-130

## Open assumptions (announced defaults)
<!-- Record any default you adopt instead of asking, so the user can veto it at the gate. -->
<!-- assumption | adopted default | rationale | reversible? -->
- Condition extensibility | Implement the seven PRD_APPENDIX condition/question variant types as built-ins, with a `metadata` field for later extension; do not implement arbitrary plugin condition types now | Keeps the platform broad enough for H1/H2/H3 and near-term experiments while avoiding unsupported public plugin semantics | yes
- Advanced semantic/NLI/Judge metrics | Define registry contracts and explicit `unsupported`/`not_computed` outputs now; implement only deterministic rule/heuristic metrics until real model/embedding work is approved | Current scope excludes LLM/API calls and PRD marks these as later/candidate evaluations | yes
- Minority candidates | Treat minority-response detection as an analysis recipe/selector, not part of core runner logic | Keeps execution general and lets future recipes reuse the selector without H-specific behavior | yes
- Follow-up | Keep limited follow-up as a recipe-triggered packet/selection and one-response artifact; do not add arbitrary multi-turn chat | PRD calls for 제한된 후속 질문 and explicitly excludes free-form long interviews from MVP | yes
- Design input format | Use JSON files for design/recipe inputs rather than YAML to avoid adding dependencies unless already present | Existing artifacts are JSON/JSONL/CSV and tests should run without new dependency decisions | yes

## Findings (cited - path:lines)
- Repository constraints still require CLI/Python MVP, local venv verification, immutable `data/raw/ko_KR.parquet`, no full raw Parquet loads, no UI, no LLM/API calls, and no API-key-dependent tests. `AGENTS.md:1-12`.
- Current implemented experiment layer already has `ProjectRecord`, `ScenarioRecord`, `QuestionSetRecord`, `RunRecord`, `ResponseRecord`, `ComparisonRecord`, and `FollowUpRecord`, but only repeat-oriented question types are represented. `src/synthetic_citizen_lab/experiments/models.py:31-271`; `src/synthetic_citizen_lab/experiments/model_types.py:31-65`.
- Current runner consumes one cohort/scenario/question set and writes `run.json` plus `responses.jsonl`; it maps `ORIGINAL` to repeat index 0 and `SAME_QUESTION_REPEAT` to repeat index 1, and rejects `FOLLOW_UP_LIMITED` in the runner. `src/synthetic_citizen_lab/experiments/runner.py:69-127`; `src/synthetic_citizen_lab/experiments/runner.py:194-205`.
- Current CLI supports `init-project`, `save-scenario`, `save-questions`, `show`, and deterministic `run`; docs explicitly say no real LLM/API calls and currently only `ORIGINAL`/`SAME_QUESTION_REPEAT`. `src/synthetic_citizen_lab/experiment_cli.py:26-116`; `docs/experiment_cli.md:1-79`.
- PRD MVP requires response analysis, minority/atypical candidates, limited follow-up, repeat comparison, and export, while its non-goals exclude public-opinion prediction, real-human equivalence, large full-population LLM calls, agent debates, long free-form interviews, and complete advanced multi-model evaluation. `docs/PRD.md:159-183`; `docs/PRD.md:209-221`.
- PRD_APPENDIX lists seven question/condition types: `ORIGINAL`, `SAME_QUESTION_REPEAT`, `PARAPHRASE`, `FRAMING_CHANGE`, `CONTEXT_CHANGE`, `SOCIAL_PRESSURE`, and `MODEL_CONDITION_CHANGE`. `docs/PRD_APPENDIX.md:9-24`.
- PRD_APPENDIX says automatic evaluation is for surfacing change/contradiction/review candidates, not final truth, and identifies initial metrics such as stance match, stance score delta, side-by-side text, contradiction candidates, and human-review need. `docs/PRD_APPENDIX.md:81-109`.
- Human evaluation should remain small, independent, and focused on consistency/contradiction/profile factual conflict/confidence; early MVP can use CSV/simple forms instead of a human-review UI. `docs/PRD_APPENDIX.md:133-186`; `docs/PRD_APPENDIX.md:330-339`.
- Metis review identified the main planning risks: H1/H2/H3 hardcoding, missing separation of design/condition/execution/analysis, under-specified condition metadata, premature LLM calls, unsafe multiplied raw-data access, vague metric contracts, and vague exports. `Metis plan-gap review ses_07232d068ffeVhDgY7b0SW8Hwk`.

## Decisions (with rationale)
- The old Wave 5 should be superseded, not extended in-place: repeat comparison/follow-up/export becomes later platform behavior built on design, condition, metric, and recipe primitives.
- H1/H2/H3 will be represented as analysis recipes/presets only. No core model, storage helper, runner branch, or metric registry code should contain H1/H2/H3-specific logic.
- Phase 5 starts with a general `ExperimentDesignRecord`/condition schema because later matrix execution and metric computation need stable IDs, provenance, and validation.
- The system remains mock-only through this plan. `MODEL_CONDITION_CHANGE` stores model-condition metadata and can affect deterministic mock behavior, but must not perform network/API calls or require `.env`.
- Question variants become condition metadata rather than only a flat `QuestionType` enum; each PRD_APPENDIX variant has required fields and validation rules.
- Automatic metrics use an explicit registry with name/version/required inputs/output schema/status. Unsupported advanced metrics are recorded as not computed rather than silently faked.
- Tidy exports and human-evaluation packets are file artifacts under `outputs/experiments/<project_id>/...`; no Streamlit, browser UI, web service, or manual UI verification is part of this plan.

## Scope IN
- Revised phase-5-and-beyond implementation plan only.
- Python/CLI/file-backed experiment platform primitives under `src/synthetic_citizen_lab/experiments/` and `src/synthetic_citizen_lab/_experiment_cli*.py`.
- Design schema, condition matrix, mock-compatible runner integration, metric registry, analysis recipes, human-evaluation packets, limited follow-up selection, minority candidate selection, and tidy exports.
- Tests and docs updates needed for a downstream worker to implement without further interview.

## Scope OUT (Must NOT have)
- Product code implementation by Prometheus.
- Streamlit, Plotly dashboards, browser UI, web service, background worker service, or manual visual QA.
- Real LLM/API calls, network calls, API-key-required tests, `.env` requirements, live provider SDK setup.
- Mutating, moving, resaving, staging, or committing `data/raw/ko_KR.parquet`; full raw Parquet memory loads.
- Core hardcoding of H1/H2/H3 in runner, storage, models, or metric internals.
- Free-form long multi-turn interviews, agent debates, social-spread simulations, population-representativeness or public-opinion-prediction claims.

## Open questions
- None blocking. Adopted defaults above are reversible and intentionally conservative for the current no-UI/no-LLM MVP scope.

## Approval gate
status: approved-and-written
<!-- When exploration is exhausted and unknowns are answered, set status: awaiting-approval. -->
<!-- That durable record is the loop guard: on a later turn read it and resume at the gate instead of re-running exploration. -->
