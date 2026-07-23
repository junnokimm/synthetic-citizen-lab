# 수정된 실험 플랫폼 개발 계획안

이 문서는 기존 `docs/PRD.md`와 `docs/PRD_APPENDIX.md`의 MVP 계획을 바탕으로, phase 5 이후 개발 방향을 어떻게 바꿔야 하는지 정리한다.

핵심 변경점은 다음과 같다.

> 기존 계획은 `ORIGINAL`과 `SAME_QUESTION_REPEAT` 중심의 반복 비교, 제한된 follow-up, export를 phase 5 이후에 추가하는 흐름이었다.  
> 수정된 계획은 이를 그대로 구현하지 않고, 질문 변형·페르소나 정보량·모델 조건·평가 지표를 조합할 수 있는 범용 실험 플랫폼으로 확장한다.

즉 H1/H2/H3를 위한 전용 시스템을 만드는 것이 아니라, H1/H2/H3를 **범용 실험 구조 위의 분석 recipe/preset**으로 표현한다.

---

## 1. 현재 구현 상태

현재 MVP는 phase 4까지 다음 기반을 갖춘 상태다.

| 영역 | 현재 상태 |
| --- | --- |
| 코호트 기반 persona context | 기존 cohort artifact를 읽고 P1/P2/P3 context를 안전하게 로드 |
| 실험 메타데이터 | project, scenario, question set, run, response record 저장 |
| CLI | `scl-experiment init-project`, `save-scenario`, `save-questions`, `show`, `run` |
| 실행기 | deterministic mock response engine |
| 실행 산출물 | `run.json`, `responses.jsonl` |
| 질문 유형 | `ORIGINAL`, `SAME_QUESTION_REPEAT` 중심 |
| 제외 범위 | Streamlit UI, 실제 LLM/API 호출, cohort sampler 신규 구현, raw Parquet 변형 |

이 기반은 유지한다. 수정 계획은 phase 4 결과를 버리는 것이 아니라, 그 위에 더 일반적인 실험 설계 계층을 추가하는 방향이다.

---

## 2. 기존 PRD 계획의 phase 5 이후 방향

기존 PRD와 기존 작업 계획에서 phase 5 이후는 대략 다음 흐름이었다.

```text
Phase 5
- 반복 안정성 분석
- ORIGINAL vs SAME_QUESTION_REPEAT 비교
- 소수·특이 반응 후보 탐색
- 제한된 follow-up

Phase 6
- CSV/JSON export
- CLI/docs 정리
```

이 계획의 중심은 다음 기능이었다.

```text
이미 생성된 응답을 비교한다.
반복 질문에서 태도나 근거가 유지되는지 본다.
소수 반응을 찾는다.
특정 응답에 제한된 후속 질문을 붙인다.
결과를 내보낸다.
```

이 접근은 PRD의 초기 MVP에는 맞지만, 이후 연구 질문이 늘어나면 한계가 있다.

---

## 3. 기존 계획의 한계

### 3.1 반복 비교 중심으로 고정될 위험

기존 phase 5는 `ORIGINAL`과 `SAME_QUESTION_REPEAT` 비교를 중심으로 한다. 이 구조로 바로 구현하면 다음 질문 유형을 자연스럽게 담기 어렵다.

- `PARAPHRASE`
- `FRAMING_CHANGE`
- `CONTEXT_CHANGE`
- `SOCIAL_PRESSURE`
- `MODEL_CONDITION_CHANGE`

PRD_APPENDIX는 이미 위 질문 유형을 후보로 제시하고 있다. 따라서 반복 비교만 먼저 하드코딩하면, 이후 프레이밍 변화나 사회적 압력 실험을 추가할 때 runner와 분석 로직을 다시 뜯어고칠 가능성이 높다.

### 3.2 H1/H2/H3 전용 코드가 생길 위험

제공된 가설은 다음처럼 해석할 수 있다.

- H1: 질문 변형, 프레이밍, 반론 압력이 응답 일관성·근거 유지·모순에 영향을 주는가?
- H2: persona 정보량 P1/P2/P3가 프로필 정합성·근거 구체성·방어성에 영향을 주는가?
- H3: 모델 선택/버전이 질문 변형 및 persona 정보량 효과를 조절하는가?

이 가설을 그대로 코드로 옮기면 다음과 같은 나쁜 구조가 생길 수 있다.

```text
run_h1_experiment()
run_h2_experiment()
run_h3_experiment()
```

이렇게 되면 시스템은 “H1/H2/H3 실험기”가 된다. 하지만 사용자가 원하는 것은 더 넓은 실험 시스템이다.

### 3.3 평가 지표가 ad hoc으로 흩어질 위험

기존 phase 5는 반복 비교 지표를 바로 계산하는 방식이었다.

예상 지표는 다음 정도였다.

- stance match
- stance score delta
- contradiction candidate
- needs human review

하지만 H1/H2/H3와 PRD_APPENDIX를 함께 보면 필요한 지표가 더 넓어진다.

- reason retention
- semantic similarity 후보
- profile consistency
- reason specificity
- defensiveness
- stance clarity
- persona attribute usage
- change justification

따라서 평가 지표를 runner 내부에 직접 넣지 말고, metric registry/evaluator 계층으로 분리해야 한다.

### 3.4 `MODEL_CONDITION_CHANGE`가 실제 API 호출로 오해될 위험

PRD_APPENDIX에는 `MODEL_CONDITION_CHANGE`가 있다. 그러나 현재 repository scope는 실제 LLM/API 호출을 제외한다.

따라서 모델 조건 비교를 지원하더라도 지금 단계에서는 다음까지만 해야 한다.

```text
model condition metadata 저장
mock engine이 model condition 값을 deterministic하게 반영
실제 provider/API 호출은 이후 별도 승인 후 구현
```

---

## 4. 수정된 핵심 방향

기존 phase 5를 다음처럼 대체한다.

```text
기존:
Phase 5 = repeat comparison + minority candidate + limited follow-up

수정:
Phase 5 = general experiment design layer
Phase 6 = condition matrix runner
Phase 7 = metric registry/evaluation layer
Phase 8 = analysis recipe/preset layer
Phase 9 = human evaluation packet
Phase 10 = tidy export
이후 = 실제 LLM/model provider integration
```

핵심 원칙은 다음과 같다.

1. H1/H2/H3는 core code가 아니라 recipe/preset이다.
2. 질문 유형은 단순 enum이 아니라 condition metadata를 가진다.
3. 실행은 condition matrix를 기반으로 한다.
4. 평가는 metric registry를 통해 수행한다.
5. advanced metric은 지금 fake로 만들지 않고 `not_computed`로 기록한다.
6. human evaluation은 UI가 아니라 CSV/JSON/Markdown packet으로 먼저 제공한다.
7. 실제 LLM/API 호출은 이 계획 밖으로 둔다.

---

## 5. 기존 계획과 수정 계획 비교

| 구분 | 기존 계획 | 수정 계획 |
| --- | --- | --- |
| phase 5의 중심 | 반복 안정성 비교 | 범용 실험 설계 schema |
| 질문 유형 | `ORIGINAL`, `SAME_QUESTION_REPEAT` 중심 | PRD_APPENDIX의 7개 유형을 조건으로 표현 |
| 실행 단위 | 단일 run | condition matrix 기반 다중 조건 run |
| H1/H2/H3 처리 | 구현 방향이 불명확, 하드코딩 위험 | analysis recipe/preset으로만 표현 |
| 평가 지표 | 반복 비교용 일부 지표 | metric registry와 evaluator contract |
| 모델 조건 | 이후 기능 또는 불명확 | metadata/mock-only로 먼저 표현 |
| follow-up | phase 5 기능 | recipe/selector 기반 제한 follow-up으로 이동 |
| 소수 반응 | 분석 기능 | analysis selector/recipe로 일반화 |
| export | 마지막 결과 내보내기 | tidy data export와 provenance 포함 |
| human review | 나중에 검토 | file-based human evaluation packet |
| UI | 없음 | 계속 없음 |
| 실제 LLM/API | 없음 | 계속 없음, 이후 별도 단계 |

---

## 6. 수정된 phase 5: General Experiment Design Layer

### 목표

질문 변형, persona 정보량, 모델 조건, 평가 지표를 하나의 실험 설계로 저장한다.

예상 추가 모델은 다음과 같다.

```text
ExperimentDesignRecord
QuestionVariantCondition
PersonaContextCondition
ModelCondition
MetricSpec
ComparisonPlan
```

### 설계가 표현해야 하는 것

```text
project_id
design_id
scenario_id
question_set_id
cohort_id
question variant conditions
persona context levels
model conditions
metric specs
analysis recipe references
export schema version
```

### 질문 variant metadata

각 질문 유형은 단순 문자열이 아니라 필요한 metadata를 가진다.

| 유형 | 필요한 metadata |
| --- | --- |
| `ORIGINAL` | 기준 질문 ID, 기준 문항 텍스트 |
| `SAME_QUESTION_REPEAT` | 원 질문 ID, repeat index |
| `PARAPHRASE` | 원 질문 ID, paraphrase text, 의미 보존 기준 |
| `FRAMING_CHANGE` | frame label, framing direction, modified text |
| `CONTEXT_CHANGE` | 추가된 맥락/조건 payload, source |
| `SOCIAL_PRESSURE` | pressure source, pressure level, pressure text |
| `MODEL_CONDITION_CHANGE` | model condition ID, model label, generation metadata |

### 중요한 guardrail

`MODEL_CONDITION_CHANGE`는 지금 실제 API 호출을 의미하지 않는다. 이 단계에서는 model condition을 저장하고 mock engine에 deterministic metadata로 전달하는 정도만 한다.

---

## 7. 수정된 phase 6: Condition Matrix Runner

### 목표

실험 설계를 실행 가능한 condition matrix로 확장한다.

예를 들어 다음 축을 조합할 수 있어야 한다.

```text
question_variant_type:
  ORIGINAL
  PARAPHRASE
  FRAMING_CHANGE
  SOCIAL_PRESSURE

persona_context_level:
  P1
  P2
  P3

model_condition:
  mock_baseline
  mock_high_consistency
  mock_pressure_sensitive
```

컴파일 결과는 다음처럼 저장한다.

```text
condition_id
design_id
scenario_id
question_id
question_variant_type
persona_context_level
model_condition_id
metric_set_id
provenance
```

### 기존 runner와의 차이

기존 runner는 다음 입력을 중심으로 했다.

```text
cohort_dir + scenario_id + question_set_id + persona_context_level + generation_config
```

수정된 runner는 다음을 중심으로 한다.

```text
design_id + compiled condition matrix + cohort artifact + mock engine
```

즉 runner가 “반복 질문인지 아닌지”를 직접 판단하는 구조에서, condition cell을 실행하는 구조로 바뀐다.

---

## 8. 수정된 phase 7: Metric Registry and Evaluation Layer

### 목표

평가 지표를 코드 여기저기에 흩뿌리지 않고 registry로 관리한다.

각 metric은 다음 계약을 가져야 한다.

```text
metric_name
metric_version
required_inputs
output_schema
status
value
details
needs_human_review
```

### 우선 구현할 deterministic/rule-based 지표

```text
stance_consistency
stance_score_delta
reason_overlap
concern_overlap
acceptance_condition_overlap
contradiction_candidate
profile_consistency_candidate
reason_specificity_score
defensiveness_score
stance_clarity_score
persona_attribute_usage
minority_response_candidate
needs_human_review
```

### 지금 구현하지 않을 advanced metric

다음은 계약만 정의하고 실제 계산은 하지 않는다.

```text
semantic_similarity
nli_contradiction
llm_judge_contradiction
llm_judge_reason_retention
```

이 지표가 요청되면 fake 값을 넣지 않고 다음처럼 기록한다.

```json
{
  "metric_name": "semantic_similarity",
  "status": "not_computed",
  "reason": "embedding provider is not available in the current no-API scope"
}
```

---

## 9. 수정된 phase 8: Analysis Recipes, Not Hardcoded Hypotheses

### 목표

H1/H2/H3를 hardcoded function이 아니라 recipe로 둔다.

나쁜 방향:

```text
run_h1_experiment()
run_h2_experiment()
run_h3_experiment()
```

좋은 방향:

```text
recipes/h1_question_variation.json
recipes/h2_persona_context_level.json
recipes/h3_model_condition_interaction.json
recipes/non_hypothesis_policy_ab_comparison.json
```

### recipe schema 예시

```json
{
  "recipe_id": "recipe_question_variation_consistency_v1",
  "group_by": ["question_variant_type", "pressure_level"],
  "compare_against": "ORIGINAL",
  "metrics": [
    "stance_consistency",
    "stance_score_delta",
    "reason_overlap",
    "contradiction_candidate",
    "needs_human_review"
  ],
  "filters": [],
  "exports": ["metric_summary_by_condition", "comparison_pairs"]
}
```

### H1 preset

```text
independent variables:
- question_variant_type
- framing_direction
- pressure_level
- counterargument_present

dependent metrics:
- stance_consistency
- stance_score_delta
- reason_overlap
- contradiction_candidate
- change_justification_candidate
- needs_human_review
```

### H2 preset

```text
independent variables:
- persona_context_level: P1/P2/P3

dependent metrics:
- profile_consistency_candidate
- reason_specificity_score
- defensiveness_score
- stance_clarity_score
- persona_attribute_usage
```

### H3 preset

```text
independent variables:
- model_condition_id
- question_variant_type
- persona_context_level

dependent metrics:
- stance_consistency
- contradiction_candidate
- reason_overlap
- profile_consistency_candidate
- defensiveness_score
```

### 비-H 가설 recipe도 반드시 포함

범용성을 증명하려면 H1/H2/H3 외 recipe가 하나 이상 있어야 한다.

예:

```text
scenario_policy_ab_comparison_v1

group_by:
- scenario_variant_label
- cohort_segment

metrics:
- stance_distribution
- concern_frequency
- acceptance_condition_frequency
- minority_response_candidate
```

---

## 10. 수정된 phase 9: Human Evaluation Packet

### 목표

사람 평가를 UI로 만들지 않고, 사람이 검토할 수 있는 artifact로 만든다.

예상 산출물:

```text
outputs/experiments/<project_id>/human_eval/<packet_id>/sample.csv
outputs/experiments/<project_id>/human_eval/<packet_id>/schema.json
outputs/experiments/<project_id>/human_eval/<packet_id>/instructions.md
```

### 포함할 정보

```text
project_id
design_id
run_id
condition_id
agent_id or anonymized_agent_id
question text
response A
response B if pairwise comparison
automatic metric outputs
human rating fields
reviewer confidence field
provenance
```

### 제외할 정보

```text
raw profile 전체 덤프
직접 식별 가능성이 있는 상세 정보
필요 이상의 persona attributes
```

인간 평가는 최종 정답 생성이 아니라 자동 평가가 표시한 후보를 검토하는 용도로 둔다.

---

## 11. 수정된 phase 10: Tidy Export

### 목표

단순한 `responses.jsonl` 내보내기를 넘어서, 분석 가능한 long-form/tidy data를 제공한다.

예상 export:

```text
design_manifest.json
condition_matrix.csv
responses_long.csv
comparisons_long.csv
metric_results_long.csv
metric_summary_by_condition.csv
minority_candidates.csv
human_eval_sample.csv
run_provenance.json
```

각 export에는 다음 provenance를 포함한다.

```text
project_id
design_id
run_id
condition_id
cohort_id
scenario_id
question_id
question_variant_type
persona_context_level
model_condition_id
metric_name
metric_version
export_schema_version
```

---

## 12. 실제 LLM/API 연동은 이후 단계

H3를 현실적으로 검증하려면 실제 모델 조건 비교가 필요하다. 하지만 현재 scope에서는 실제 LLM/API 호출을 넣지 않는다.

권장 순서는 다음과 같다.

```text
1. mock-only condition/design/evaluation/export 구조 안정화
2. model condition metadata와 provenance 검증
3. 실제 LLM provider abstraction 설계
4. API key 없는 테스트와 API key 있는 선택적 integration test 분리
5. 실제 provider별 runner 추가
```

따라서 지금 문서의 “model condition”은 실제 API 호출이 아니라, 향후 실제 모델 비교를 담기 위한 schema와 artifact 준비를 의미한다.

---

## 13. follow-up 기능의 위치 변경

기존 계획에서는 limited follow-up이 phase 5의 핵심 기능이었다.

수정 계획에서는 follow-up을 다음처럼 이동한다.

```text
기존:
repeat comparison과 함께 바로 follow-up 실행

수정:
metric/recipe/selector 결과로 follow-up 후보를 고르고,
선택된 parent response에 대해 제한된 1회 follow-up artifact 생성
```

즉 follow-up은 독립 대화 기능이 아니라, 분석 결과를 더 깊게 보기 위한 제한된 탐색 기능이다.

---

## 14. 소수·특이 반응 기능의 위치 변경

기존 계획에서는 소수 반응 후보 탐색이 phase 5 분석 기능이었다.

수정 계획에서는 이를 recipe/selector로 일반화한다.

예:

```text
minority selector:
- group_by: condition_id or cohort segment
- signature fields: stance, concerns, acceptance_conditions
- threshold: frequency <= 1 or bottom quantile
- output: minority_candidates.csv
```

이렇게 하면 H1/H2/H3뿐 아니라 일반 정책 A/B 비교나 서비스 기능 비교에도 같은 selector를 재사용할 수 있다.

---

## 15. 데이터 안전 및 scope guardrail

수정된 계획에서도 다음 제약은 그대로 유지한다.

- `data/raw/ko_KR.parquet`는 수정, 이동, 재저장, stage, commit하지 않는다.
- raw Parquet 전체를 메모리에 로드하지 않는다.
- 데이터 작업은 PyArrow/DuckDB metadata, projection, filter, sampling, small `LIMIT` preview 중심으로만 한다.
- Streamlit UI는 포함하지 않는다.
- 실제 LLM/API 호출은 포함하지 않는다.
- `.env`나 API key 없이 테스트가 통과해야 한다.
- 결과는 실제 한국 시민 여론 예측으로 해석하지 않는다.

---

## 16. 최종 수정 roadmap

| 단계 | 이름 | 핵심 산출물 |
| --- | --- | --- |
| Phase 5 | General Experiment Design | design schema, condition metadata, design storage |
| Phase 6 | Condition Matrix Runner | condition matrix, matrix run artifacts, mock-compatible model conditions |
| Phase 7 | Metric Registry | metric specs, deterministic evaluators, not-computed advanced metrics |
| Phase 8 | Analysis Recipes | H1/H2/H3 presets, non-H recipe, minority/follow-up selectors |
| Phase 9 | Human Evaluation Packet | sample CSV, schema JSON, instructions MD |
| Phase 10 | Tidy Export | long-form CSV/JSONL exports with provenance |
| Later | Live Model Integration | provider abstraction, real LLM runner, API-key-separated tests |

---

## 17. 한 줄 결론

기존 phase 5 이후 계획은 “반복 비교와 follow-up을 붙이는 MVP 마무리”였지만, 수정된 계획은 “다양한 질문 변형, persona 정보량, 모델 조건, 평가 지표를 조합할 수 있는 범용 실험 플랫폼”으로 전환한다.

이렇게 해야 H1/H2/H3뿐 아니라 이후의 정책 A/B 비교, 서비스 기능 비교, 프레이밍 민감도 실험, 사회적 압력 실험, 모델 조건 비교를 같은 구조 위에서 실행할 수 있다.
