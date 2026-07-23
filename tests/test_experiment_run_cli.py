import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
from _pytest.capture import CaptureFixture

from synthetic_citizen_lab.cohort.models import (
    CohortFilter,
    CohortRequest,
    SamplingSpec,
)
from synthetic_citizen_lab.cohort.sampler import CohortSampler
from synthetic_citizen_lab.experiment_cli import main
from synthetic_citizen_lab.experiments.storage import (
    load_response_records,
    load_run_record,
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


def test_cli_run_executes_mock_responses(
    tmp_path: Path,
    capsys: CaptureFixture[str],
) -> None:
    output_root = tmp_path / "outputs" / "experiments"
    cohort_source = tmp_path / "fixture.parquet"
    cohort_output_root = tmp_path / "cohorts"
    _write_context_fixture(cohort_source)
    cohort_dir = CohortSampler(cohort_source).save_sample(
        CohortRequest(
            name="cli run fixture",
            filters=CohortFilter(),
            sampling=SamplingSpec(sample_size=2, seed=7),
        ),
        output_dir=cohort_output_root,
    )

    assert main(
        (
            "init-project",
            "--output-dir",
            str(output_root),
            "--project-id",
            "project_stage4",
            "--name",
            "mobility pilot",
            "--research-goal",
            "Explore synthetic persona reactions to a transport policy.",
            "--non-claim",
            "Synthetic pretest only.",
        )
    ) == 0
    capsys.readouterr()

    assert main(
        (
            "save-scenario",
            "--output-dir",
            str(output_root),
            "--project-id",
            "project_stage4",
            "--scenario-id",
            "scenario_mobility_v1",
            "--title",
            "mobility support policy",
            "--variant",
            "A|Baseline support text.",
            "--variant",
            "B|Expanded support text.",
        )
    ) == 0
    capsys.readouterr()

    assert main(
        (
            "save-questions",
            "--output-dir",
            str(output_root),
            "--project-id",
            "project_stage4",
            "--question-set-id",
            "question_set_mobility_v1",
            "--name",
            "mobility question set",
            "--question",
            (
                "question_main_original_v1|ORIGINAL|"
                "이 정책에 대한 입장과 이유를 말해 주세요."
            ),
            "--question",
            (
                "question_main_repeat_v1|SAME_QUESTION_REPEAT|"
                "같은 질문에 다시 답해 주세요.|question_main_original_v1"
            ),
        )
    ) == 0
    capsys.readouterr()

    exit_code = main(
        (
            "run",
            "--cohort-dir",
            str(cohort_dir),
            "--output-dir",
            str(output_root),
            "--project-id",
            "project_stage4",
            "--run-id",
            "run_stage4_001",
            "--scenario-id",
            "scenario_mobility_v1",
            "--question-set-id",
            "question_set_mobility_v1",
            "--seed",
            "11",
        )
    )

    assert exit_code == 0
    cli_output = capsys.readouterr().out.splitlines()
    output_map = dict(line.split("=", maxsplit=1) for line in cli_output)
    run_path = Path(output_map["run_path"])
    responses_path = Path(output_map["responses_path"])
    run_record = load_run_record(run_path)
    responses = load_response_records(responses_path)

    assert run_record.run_id == "run_stage4_001"
    assert run_record.repeat_count == 2
    assert len(responses) == 4
    assert all(response.response_text for response in responses)


def test_cli_run_help_lists_required_fields(capsys: CaptureFixture[str]) -> None:
    exit_code = main(("run", "--help"))

    assert exit_code == 0
    help_payload = json.loads(capsys.readouterr().out)
    assert help_payload["command"] == "run"
    assert "--cohort-dir" in help_payload["required"]
