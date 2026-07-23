from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from tests.experiment_fixtures import (
    build_project_record,
    build_question_set_record,
    build_scenario_record,
)

from synthetic_citizen_lab.cohort.models import (
    CohortFilter,
    CohortRequest,
    SamplingSpec,
)
from synthetic_citizen_lab.cohort.sampler import CohortSampler
from synthetic_citizen_lab.cohort.storage import load_cohort_definition
from synthetic_citizen_lab.experiments.context_models import (
    PersonaContextLevel,
    PersonaId,
)
from synthetic_citizen_lab.experiments.engines import MockResponseEngine
from synthetic_citizen_lab.experiments.models import GenerationConfig
from synthetic_citizen_lab.experiments.runner import (
    RunExperimentRequest,
    run_experiment,
)
from synthetic_citizen_lab.experiments.storage import (
    load_project_record,
    load_question_set_record,
    load_response_records,
    load_run_record,
    load_scenario_record,
    write_project_record,
    write_question_set_record,
    write_scenario_record,
)


def _write_context_fixture(path: Path) -> None:
    table = pa.table(
        {
            "uuid": pa.array(["p1", "p2"]),
            "age": pa.array([25, 45], type=pa.int64()),
            "sex": pa.array(["여자", "남자"]),
            "region": pa.array(["서울", "서울"]),
            "district": pa.array(["강남구", "마포구"]),
            "marital_status": pa.array(["미혼", "기혼"]),
            "education_level": pa.array(["고등학교", "대학원"]),
            "bachelors_field": pa.array(["해당없음", "공학"]),
            "occupation": pa.array(["자영업자", "회사원"]),
            "family_type": pa.array(["1인가구", "부부+자녀"]),
            "housing_type": pa.array(["아파트", "아파트"]),
            "housing_tenure": pa.array(["자가", "전세"]),
            "military_status": pa.array(["해당없음", "군필"]),
            "economic_activity_status": pa.array(["취업자", "취업자"]),
            "income_bracket": pa.array(["150~250만원", "350~450만원"]),
            "bmi_status": pa.array(["정상", "비만"]),
            "blood_pressure_status": pa.array(["정상", "고혈압"]),
            "blood_sugar_status": pa.array(["정상", "당뇨"]),
            "waist_status": pa.array(["정상", "복부비만"]),
            "smoking_status": pa.array(["비흡연", "현재흡연"]),
            "drinking_status": pa.array(["비음주", "음주"]),
            "openness": pa.array(
                [
                    '{"t_score": 40, "label": "낮음"}',
                    '{"t_score": 55, "label": "높음"}',
                ]
            ),
            "conscientiousness": pa.array(['{"t_score": 50, "label": "보통"}'] * 2),
            "extraversion": pa.array(['{"t_score": 50, "label": "보통"}'] * 2),
            "agreeableness": pa.array(['{"t_score": 50, "label": "보통"}'] * 2),
            "neuroticism": pa.array(['{"t_score": 50, "label": "보통"}'] * 2),
        }
    )
    pq.write_table(table, path)


@pytest.fixture
def sampled_cohort_dir(tmp_path: Path) -> Path:
    source_path = tmp_path / "fixture.parquet"
    output_dir = tmp_path / "cohorts"
    _write_context_fixture(source_path)
    return CohortSampler(source_path).save_sample(
        CohortRequest(
            name="runner fixture",
            filters=CohortFilter(),
            sampling=SamplingSpec(sample_size=2, seed=7),
        ),
        output_dir=output_dir,
    )


def _write_experiment_records(output_root: Path) -> None:
    write_project_record(
        output_root,
        build_project_record().model_copy(update={"project_id": "project_stage4"}),
    )
    write_scenario_record(
        output_root,
        build_scenario_record().model_copy(update={"project_id": "project_stage4"}),
    )
    write_question_set_record(
        output_root,
        build_question_set_record().model_copy(update={"project_id": "project_stage4"}),
    )


def test_runner_writes_run_and_response_artifacts(
    sampled_cohort_dir: Path,
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "experiments"
    _write_experiment_records(output_root)

    artifacts = run_experiment(
        RunExperimentRequest(
            output_root=output_root,
            cohort_dir=sampled_cohort_dir,
            project_id="project_stage4",
            run_id="run_stage4_001",
            scenario_id="scenario_healthcare_v1",
            question_set_id="question_set_main_v1",
            persona_context_level=PersonaContextLevel.P2,
            generation_config=GenerationConfig(
                model="mock-model",
                temperature=0.3,
                prompt_version="prompt_v1",
            ),
            seed=11,
        ),
        response_engine=MockResponseEngine(),
    )

    cohort_definition = load_cohort_definition(sampled_cohort_dir / "cohort.json")
    loaded_project = load_project_record(
        output_root / "project_stage4" / "project.json"
    )
    loaded_scenario = load_scenario_record(
        output_root
        / "project_stage4"
        / "scenarios"
        / "scenario_healthcare_v1.json"
    )
    loaded_question_set = load_question_set_record(
        output_root
        / "project_stage4"
        / "question_sets"
        / "question_set_main_v1.json"
    )
    run_record = load_run_record(artifacts.run_path)
    responses = load_response_records(artifacts.responses_path)

    assert loaded_project.project_id == "project_stage4"
    assert loaded_scenario.scenario_id == "scenario_healthcare_v1"
    assert loaded_question_set.question_set_id == "question_set_main_v1"
    assert run_record.cohort_id == cohort_definition.cohort_id
    assert run_record.repeat_count == 2
    assert len(responses) == 4
    assert tuple(response.repeat_index for response in responses) == (0, 1, 0, 1)
    assert all(response.status.value == "success" for response in responses)


def test_runner_records_engine_errors_without_aborting(
    sampled_cohort_dir: Path,
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "experiments"
    _write_experiment_records(output_root)

    artifacts = run_experiment(
        RunExperimentRequest(
            output_root=output_root,
            cohort_dir=sampled_cohort_dir,
            project_id="project_stage4",
            run_id="run_stage4_002",
            scenario_id="scenario_healthcare_v1",
            question_set_id="question_set_main_v1",
            persona_context_level=PersonaContextLevel.P2,
            generation_config=GenerationConfig(
                model="mock-model",
                temperature=0.3,
                prompt_version="prompt_v1",
            ),
            seed=11,
        ),
        response_engine=MockResponseEngine(
            failure_persona_ids=frozenset({PersonaId("p1")})
        ),
    )

    responses = load_response_records(artifacts.responses_path)

    assert len(responses) == 4
    assert sum(response.status.value == "error" for response in responses) == 2
    assert sum(response.status.value == "success" for response in responses) == 2
    assert all(
        response.error_type == "ResponseGenerationError"
        for response in responses
        if response.status.value == "error"
    )
