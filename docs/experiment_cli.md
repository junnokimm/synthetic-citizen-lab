# Phase 3 Experiment CLI

`scl-experiment` manages experiment metadata artifacts under `outputs/experiments`.

Phase 4 adds deterministic mock execution on top of the phase-3 metadata surface.
The CLI still does not call a real LLM or API.

## Commands

```bash
.venv/bin/scl-experiment init-project \
  --project-id project_mobility_v1 \
  --name "mobility pilot" \
  --research-goal "Explore synthetic persona reactions to a transport policy." \
  --non-claim "Synthetic pretest only."

.venv/bin/scl-experiment save-scenario \
  --project-id project_mobility_v1 \
  --scenario-id scenario_mobility_v1 \
  --title "mobility support policy" \
  --variant "A|Baseline support text." \
  --variant "B|Expanded support text."

.venv/bin/scl-experiment save-questions \
  --project-id project_mobility_v1 \
  --question-set-id question_set_mobility_v1 \
  --name "mobility question set" \
  --question "question_main_original_v1|ORIGINAL|이 정책에 대한 입장과 이유를 말해 주세요." \
  --question "question_main_repeat_v1|SAME_QUESTION_REPEAT|같은 질문에 다시 답해 주세요.|question_main_original_v1"

.venv/bin/scl-experiment show project \
  --project-id project_mobility_v1

.venv/bin/scl-experiment show scenario \
  --project-id project_mobility_v1 \
  --scenario-id scenario_mobility_v1

.venv/bin/scl-experiment show question-set \
  --project-id project_mobility_v1 \
  --question-set-id question_set_mobility_v1

.venv/bin/scl-experiment run \
  --cohort-dir outputs/cohorts/cohort_123 \
  --project-id project_mobility_v1 \
  --run-id run_mobility_001 \
  --scenario-id scenario_mobility_v1 \
  --question-set-id question_set_mobility_v1 \
  --seed 7
```

## Requirements

- `save-scenario` and `save-questions` require an existing `project.json` created
  by `init-project`.
- `show scenario` requires `--scenario-id`.
- `show question-set` requires `--question-set-id`.
- `run` requires an existing cohort artifact plus existing project/scenario/question-set artifacts.

## Supported question types

- `ORIGINAL`
- `SAME_QUESTION_REPEAT`

Phase 3 explicitly rejects:

- `PARAPHRASE`
- `FOLLOW_UP_LIMITED`

Those surfaces belong to later phases.

## Run output

`run` writes canonical phase-4 artifacts under:

- `outputs/experiments/<project_id>/runs/<run_id>/run.json`
- `outputs/experiments/<project_id>/runs/<run_id>/responses.jsonl`

The current runner is mock-only and deterministic. The same cohort, scenario,
question set, and seed produce stable stored responses.
