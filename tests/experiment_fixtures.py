from datetime import UTC, datetime

from synthetic_citizen_lab.experiments.context_models import PersonaContextLevel
from synthetic_citizen_lab.experiments.models import (
    AutomaticEvaluationRecord,
    ComparisonRecord,
    FollowUpRecord,
    GenerationConfig,
    HumanEvaluationRecord,
    ProjectRecord,
    QuestionRecord,
    QuestionRelation,
    QuestionSetRecord,
    QuestionType,
    ResponseRecord,
    ResponseStatus,
    ReviewStatus,
    RunRecord,
    ScenarioRecord,
    ScenarioVariantLabel,
    ScenarioVariantRecord,
    StructuredResponse,
)

FIXED_NOW = datetime(2026, 7, 20, 12, 0, tzinfo=UTC)


def build_project_record() -> ProjectRecord:
    return ProjectRecord(
        project_id="project_stage2",
        name="healthcare pilot",
        research_goal="Explore synthetic persona reactions to a service policy.",
        non_claim="Synthetic pretest only.",
        created_at=FIXED_NOW,
    )


def build_scenario_record() -> ScenarioRecord:
    return ScenarioRecord(
        project_id="project_stage2",
        scenario_id="scenario_healthcare_v1",
        title="healthcare copay policy",
        variants=(
            ScenarioVariantRecord(
                variant_id="scenario_healthcare_v1_a",
                label=ScenarioVariantLabel.A,
                text="Policy explanation A.",
            ),
            ScenarioVariantRecord(
                variant_id="scenario_healthcare_v1_b",
                label=ScenarioVariantLabel.B,
                text="Policy explanation B.",
            ),
        ),
        created_at=FIXED_NOW,
    )


def build_question_set_record() -> QuestionSetRecord:
    return QuestionSetRecord(
        project_id="project_stage2",
        question_set_id="question_set_main_v1",
        name="main question set",
        questions=(
            QuestionRecord(
                question_id="question_main_original_v1",
                question_text="이 정책에 대한 입장과 이유를 말해 주세요.",
                question_type=QuestionType.ORIGINAL,
            ),
            QuestionRecord(
                question_id="question_main_repeat_v1",
                question_text="같은 질문에 다시 답해 주세요.",
                question_type=QuestionType.SAME_QUESTION_REPEAT,
                repeat_of_question_id="question_main_original_v1",
            ),
        ),
        created_at=FIXED_NOW,
    )


def build_run_record() -> RunRecord:
    return RunRecord(
        project_id="project_stage2",
        run_id="run_20260720_001",
        cohort_id="cohort_stage2_a",
        scenario_id="scenario_healthcare_v1",
        question_set_id="question_set_main_v1",
        persona_context_level=PersonaContextLevel.P2,
        generation_config=GenerationConfig(
            model="mock-model",
            temperature=0.3,
            prompt_version="prompt_v1",
        ),
        seed=7,
        repeat_count=2,
        created_at=FIXED_NOW,
    )


def build_success_response_record() -> ResponseRecord:
    return ResponseRecord(
        project_id="project_stage2",
        cohort_id="cohort_stage2_a",
        agent_id="persona_uuid_001",
        scenario_id="scenario_healthcare_v1",
        question_id="question_main_original_v1",
        run_id="run_20260720_001",
        response_id="response_001",
        repeat_index=0,
        question_type=QuestionType.ORIGINAL,
        response_text="정책 취지는 이해하지만 지금 조건에서는 반대합니다.",
        structured_response=StructuredResponse(
            stance="oppose",
            stance_score=2,
            reasoning_summary="비용 부담과 시행 준비 부족이 우려됨",
            concerns=("비용 부담", "준비 부족"),
            acceptance_conditions=("단계적 시행",),
        ),
        generation_config=GenerationConfig(
            model="mock-model",
            temperature=0.3,
            prompt_version="prompt_v1",
        ),
        status=ResponseStatus.SUCCESS,
        error_type=None,
        created_at=FIXED_NOW,
    )


def build_response_records() -> tuple[ResponseRecord, ...]:
    return (
        build_success_response_record(),
        ResponseRecord(
            project_id="project_stage2",
            cohort_id="cohort_stage2_a",
            agent_id="persona_uuid_001",
            scenario_id="scenario_healthcare_v1",
            question_id="question_main_repeat_v1",
            run_id="run_20260720_001",
            response_id="response_002",
            repeat_index=1,
            question_type=QuestionType.SAME_QUESTION_REPEAT,
            response_text="부분적으로는 동의하지만 비용이 여전히 걱정됩니다.",
            structured_response=StructuredResponse(
                stance="neutral",
                stance_score=3,
                reasoning_summary="비용 우려는 남지만 취지는 수용 가능",
                concerns=("비용 부담",),
                acceptance_conditions=("보조금",),
            ),
            generation_config=GenerationConfig(
                model="mock-model",
                temperature=0.3,
                prompt_version="prompt_v1",
            ),
            status=ResponseStatus.SUCCESS,
            error_type=None,
            created_at=FIXED_NOW,
        ),
    )


def build_comparison_record() -> ComparisonRecord:
    return ComparisonRecord(
        comparison_id="comparison_001",
        project_id="project_stage2",
        run_id="run_20260720_001",
        agent_id="persona_uuid_001",
        response_a_id="response_001",
        response_b_id="response_002",
        question_relation=QuestionRelation.SAME_QUESTION_REPEAT,
        automatic_evaluation=AutomaticEvaluationRecord(
            stance_match=False,
            stance_score_delta=1,
            contradiction_candidate=False,
            needs_human_review=True,
        ),
        human_evaluation=HumanEvaluationRecord(
            review_status=ReviewStatus.NOT_REVIEWED,
        ),
        created_at=FIXED_NOW,
    )


def build_follow_up_record() -> FollowUpRecord:
    return FollowUpRecord(
        follow_up_id="follow_up_001",
        project_id="project_stage2",
        run_id="run_20260720_001",
        parent_response_id="response_001",
        agent_id="persona_uuid_001",
        question_id="question_follow_up_001",
        question_text="어떤 보완책이 있으면 수용 가능합니까?",
        response_id="response_follow_up_001",
        created_at=FIXED_NOW,
    )
