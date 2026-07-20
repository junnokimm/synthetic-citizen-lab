---
slug: synthetic-citizen-mvp
status: planned
intent: clear
pending-action: write .omo/plans/synthetic-citizen-mvp.md
approach: Deliver the PRD in phased waves on top of the existing safe data/cohort CLI foundation: first stabilize experiment-domain data models and storage, then add scenario/question management, then add bounded response generation, then comparison/follow-up/repeat analysis, and defer richer UI and advanced evaluation to later waves unless explicitly pulled into MVP.
---

# Draft: synthetic-citizen-mvp

## Components (topology ledger)
<!-- Lock the SHAPE before depth. One row per top-level component that can succeed or fail independently. -->
<!-- id | outcome (one line) | status: active|deferred | evidence path -->
- C1 | Safe source inspection and data dictionary generation remain stable and reused by later experiment flows | active | README.md:24-40; src/synthetic_citizen_lab/cli.py:1-85; src/synthetic_citizen_lab/data/models.py:1-71; tests/test_data_inspector.py:26-69
- C2 | Category profiling remains a standalone bounded analysis surface for cohort understanding | active | README.md:33-40; src/synthetic_citizen_lab/profile_cli.py:1-76; src/synthetic_citizen_lab/data/:1; tests/test_category_profile.py:1-999
- C3 | Cohort filter/query/sampling backbone provides reproducible cohort selection and safe exports | active | README.md:42-56; src/synthetic_citizen_lab/cohort/models.py:48-198; src/synthetic_citizen_lab/cohort/sampler.py:37-167; docs/cohort_sampler.md:1-34; tests/test_cohort_sampler.py:113-264
- C4 | Scenario/question/run/response storage layer adds traceable experiment records required by the PRD | active | docs/PRD.md:83-90; docs/PRD.md:259-292; docs/PRD_APPENDIX.md:190-277
- C5 | Response generation, follow-up, repeat-run comparison, and minority-response analysis add the actual research loop | active | docs/PRD.md:83-90; docs/PRD.md:294-345; docs/PRD_APPENDIX.md:9-131; docs/PRD_APPENDIX.md:280-339
- C6 | Research UI and human-review workflow are optional delivery surfaces, not prerequisites for the first engine milestone | deferred | docs/PRD_APPENDIX.md:280-339; README.md:58-63

## Open assumptions (announced defaults)
<!-- Record any default you adopt instead of asking, so the user can veto it at the gate. -->
<!-- assumption | adopted default | rationale | reversible? -->
- Delivery surface | Backend/CLI-first before any Streamlit UI | Current repo is entirely Python package + CLI and README explicitly says Streamlit dashboard is not implemented yet | yes
- Experiment persistence | File-based JSON/CSV artifacts under outputs/ before introducing a database | Matches current cohort artifact pattern and lowers architectural risk for MVP research tooling | yes
- Structured response schema | Start with minimal schema: stance, stance_score, reasoning_summary, concerns, acceptance_conditions | PRD Appendix already sketches this exact shape and it is sufficient for comparison/repeat workflows | yes
- Automatic evaluation scope | MVP uses rule-based/structured comparisons first; advanced NLI or LLM judge stays post-MVP unless explicitly requested | Appendix marks them as candidate/after-MVP and current repo has no model-eval stack yet | yes

## Findings (cited - path:lines)
- The project is a research MVP and explicitly does not claim to predict real citizen opinion or acceptance rates. README.md:3-12
- The currently implemented CLI surface is inspection, category profiling, and cohort counting/sampling only. README.md:24-56; pyproject.toml:19-22
- README explicitly says Streamlit dashboard, response engines or LLM calls, and experiment runner/exports are intentionally not implemented yet. README.md:58-63
- PRD MVP requires a wider flow: cohort 구성 → 반응 생성 → 전체·코호트별 비교 → 특정 에이전트 조회 → 동일 질문 반복 비교. docs/PRD.md:203-221
- PRD functional requirements add missing domains: scenario/question versioning, agent response generation/storage, whole/cohort/alternative analysis, follow-up questioning, repeat comparison, and result export. docs/PRD.md:259-345
- PRD Appendix already proposes durable experiment identifiers and JSON structures for project/cohort/scenario/question/run/response/comparison, but the current codebase has no corresponding modules or tests. docs/PRD_APPENDIX.md:190-277; src/synthetic_citizen_lab:1; tests:1
- Current code already has a strong reproducibility substrate: canonical cohort filter JSON, source SHA-256 fingerprinting, deterministic seeded sampling, and saved cohort artifacts. src/synthetic_citizen_lab/cohort/models.py:140-198; src/synthetic_citizen_lab/cohort/sampler.py:54-167; tests/test_cohort_sampler.py:202-264
- Current code already enforces key safety rules aligned with the PRD, including immutable raw Parquet handling, safe preview export, and no full-memory raw-data workflow. README.md:64-72; docs/PRD.md:421-449; src/synthetic_citizen_lab/cohort/storage.py:30-43; tests/test_cohort_sampler.py:233-247
- PRD is directionally valid because it extends the current strengths instead of contradicting them: reproducible cohorting and safe bounded data access are already present, which are the hardest prerequisites for later experiment traces. README.md:42-56; docs/PRD.md:81-90; src/synthetic_citizen_lab/cohort/sampler.py:130-167
- The main feasibility risk is scope breadth: one MVP document currently bundles engine, persistence, comparison, follow-up, repeat analysis, export, and possible UI concepts, while the codebase only covers the pre-experiment data/cohort slice. docs/PRD.md:163-171; docs/PRD.md:211-221; README.md:24-63

## Decisions (with rationale)
- The PRD is broadly 타당하다: it builds on a real implemented foundation (safe inspection/profiling/cohort sampling) and the proposed research loop is coherent with the repository’s stated non-claim and data-safety posture.
- The PRD is too large to treat as a single implementation wave. A realistic plan should split it into engine-first waves so each wave ends in a usable research capability with tests.
- The next implementation milestone should not start with UI. The highest-leverage missing layer is experiment-domain storage and traceability, because every later feature depends on being able to relate cohort, scenario, question, run, and response records.
- Follow-up questions and repeat-stability analysis should be built on the same response-record model, not as separate ad hoc features.
- Advanced automatic evaluation (NLI, LLM Judge, semantic distance) should not be required for the first MVP unless you explicitly want them in scope now.
- User approved the recommended defaults: backend/CLI-first, `ORIGINAL + SAME_QUESTION_REPEAT` only, and TDD for new domain logic.
- Plan written to `.omo/plans/synthetic-citizen-mvp.md` with file-backed storage and mock-only response generation for this MVP.

## Scope IN
- PRD-to-code gap analysis
- Feasibility review grounded in current repository evidence
- Phased development approach for a backend/CLI-first MVP
- Explicit owner-decision questions that materially change the plan

## Scope OUT (Must NOT have)
- Product code changes
- Silent assumption that the current repo already supports response generation or dashboards
- Automatic expansion to advanced evaluation, multi-model comparison, or free-form long interviews without explicit approval

## Open questions
- None. The user accepted all three recommended directions.

## Approval gate
status: approved-and-written
<!-- When exploration is exhausted and unknowns are answered, set status: awaiting-approval. -->
<!-- That durable record is the loop guard: on a later turn read it and resume at the gate instead of re-running exploration. -->
