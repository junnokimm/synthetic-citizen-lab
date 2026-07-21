import pytest
from pydantic import ValidationError
from tests.experiment_fixtures import (
    FIXED_NOW,
    build_project_record,
    build_question_set_record,
    build_run_record,
    build_scenario_record,
    build_success_response_record,
)

from synthetic_citizen_lab.experiments.context_models import PersonaContextLevel
from synthetic_citizen_lab.experiments.models import (
    AutomaticEvaluationRecord,
    ComparisonRecord,
    GenerationConfig,
    HumanEvaluationRecord,
    QuestionRecord,
    QuestionRelation,
    QuestionSetRecord,
    QuestionType,
    ResponseRecord,
    ResponseStatus,
    ReviewStatus,
    ScenarioRecord,
    ScenarioVariantLabel,
    ScenarioVariantRecord,
)


def test_records_validate_happy_path() -> None:
    project = build_project_record()
    scenario = build_scenario_record()
    question_set = build_question_set_record()
    run = build_run_record()
    response = build_success_response_record()
    comparison = ComparisonRecord(
        comparison_id="comparison_001",
        project_id="project_stage2",
        run_id="run_20260720_001",
        agent_id="persona_uuid_001",
        response_a_id="response_001",
        response_b_id="response_002",
        question_relation=QuestionRelation.SAME_QUESTION_REPEAT,
        automatic_evaluation=AutomaticEvaluationRecord(
            stance_match=True,
            stance_score_delta=1,
            contradiction_candidate=False,
            needs_human_review=False,
        ),
        human_evaluation=HumanEvaluationRecord(
            review_status=ReviewStatus.NOT_REVIEWED,
        ),
        created_at=FIXED_NOW,
    )

    assert project.project_id == "project_stage2"
    assert scenario.variants[0].label is ScenarioVariantLabel.A
    assert (
        question_set.questions[1].repeat_of_question_id
        == "question_main_original_v1"
    )
    assert run.persona_context_level is PersonaContextLevel.P2
    assert response.structured_response.stance_score == 2
    assert comparison.automatic_evaluation.stance_match is True


def test_scenario_record_rejects_duplicate_variant_labels() -> None:
    with pytest.raises(ValidationError, match="duplicate scenario variant labels"):
        ScenarioRecord(
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
                    variant_id="scenario_healthcare_v1_alt_a",
                    label=ScenarioVariantLabel.A,
                    text="Policy explanation alternate A.",
                ),
            ),
            created_at=FIXED_NOW,
        )


def test_question_set_rejects_missing_repeat_reference() -> None:
    with pytest.raises(ValidationError, match="repeat_of_question_id"):
        QuestionSetRecord(
            project_id="project_stage2",
            question_set_id="question_set_main_v1",
            name="main question set",
            questions=(
                QuestionRecord(
                    question_id="question_main_repeat_v1",
                    question_text="같은 질문에 다시 답해 주세요.",
                    question_type=QuestionType.SAME_QUESTION_REPEAT,
                    repeat_of_question_id="missing_original_id",
                ),
            ),
            created_at=FIXED_NOW,
        )


def test_response_record_requires_error_type_for_error_status() -> None:
    with pytest.raises(ValidationError, match="error_type"):
        ResponseRecord(
            project_id="project_stage2",
            cohort_id="cohort_stage2_a",
            agent_id="persona_uuid_001",
            scenario_id="scenario_healthcare_v1",
            question_id="question_main_original_v1",
            run_id="run_20260720_001",
            response_id="response_001",
            repeat_index=0,
            question_type=QuestionType.ORIGINAL,
            response_text=None,
            structured_response=None,
            generation_config=GenerationConfig(
                model="mock-model",
                temperature=0.3,
                prompt_version="prompt_v1",
            ),
            status=ResponseStatus.ERROR,
            error_type=None,
            created_at=FIXED_NOW,
        )


def test_comparison_record_rejects_same_response_pair() -> None:
    with pytest.raises(ValidationError, match="response_a_id"):
        ComparisonRecord(
            comparison_id="comparison_001",
            project_id="project_stage2",
            run_id="run_20260720_001",
            agent_id="persona_uuid_001",
            response_a_id="response_001",
            response_b_id="response_001",
            question_relation=QuestionRelation.SAME_QUESTION_REPEAT,
            automatic_evaluation=AutomaticEvaluationRecord(
                stance_match=True,
                stance_score_delta=1,
                contradiction_candidate=False,
                needs_human_review=False,
            ),
            human_evaluation=HumanEvaluationRecord(
                review_status=ReviewStatus.NOT_REVIEWED,
            ),
            created_at=FIXED_NOW,
        )
