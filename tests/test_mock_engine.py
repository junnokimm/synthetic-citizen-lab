import pytest
from tests.experiment_fixtures import (
    build_question_set_record,
    build_run_record,
    build_scenario_record,
)

from synthetic_citizen_lab.experiments.context_models import PersonaContextP2, PersonaId
from synthetic_citizen_lab.experiments.engines import (
    EngineRequest,
    MockResponseEngine,
    ResponseGenerationError,
)


def _build_persona_context() -> PersonaContextP2:
    return PersonaContextP2(
        persona_id=PersonaId("persona_uuid_001"),
        age=45,
        sex="남자",
        region="서울",
        district="마포구",
        marital_status="기혼",
        education_level="대학원",
        bachelors_field="공학",
        occupation="회사원",
        family_type="부부+자녀",
        housing_type="아파트",
        housing_tenure="전세",
        military_status="군필",
        economic_activity_status="취업자",
        income_bracket="350~450만원",
        bmi_status="비만",
        blood_pressure_status="고혈압",
        blood_sugar_status="당뇨",
        waist_status="복부비만",
        smoking_status="현재흡연",
        drinking_status="음주",
        openness='{"t_score": 55, "label": "높음"}',
        conscientiousness='{"t_score": 50, "label": "보통"}',
        extraversion='{"t_score": 50, "label": "보통"}',
        agreeableness='{"t_score": 50, "label": "보통"}',
        neuroticism='{"t_score": 50, "label": "보통"}',
    )


def test_mock_response_engine_is_deterministic_for_same_request() -> None:
    question = build_question_set_record().questions[0]
    request = EngineRequest(
        persona_context=_build_persona_context(),
        scenario=build_scenario_record(),
        question=question,
        run=build_run_record(),
        repeat_index=0,
    )
    engine = MockResponseEngine()

    first_response = engine.generate_response(request)
    second_response = engine.generate_response(request)

    assert first_response == second_response
    assert first_response.response_text
    assert first_response.structured_response.reasoning_summary


def test_mock_response_engine_failure_persona_raises() -> None:
    question = build_question_set_record().questions[1]
    request = EngineRequest(
        persona_context=_build_persona_context(),
        scenario=build_scenario_record(),
        question=question,
        run=build_run_record(),
        repeat_index=1,
    )
    engine = MockResponseEngine(
        failure_persona_ids=frozenset({PersonaId("persona_uuid_001")})
    )

    with pytest.raises(ResponseGenerationError, match="persona_uuid_001"):
        engine.generate_response(request)
