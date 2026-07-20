import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from synthetic_citizen_lab.cohort.constants import NARRATIVE_COLUMNS
from synthetic_citizen_lab.cohort.models import (
    CohortFilter,
    CohortRequest,
    SamplingSpec,
)
from synthetic_citizen_lab.cohort.sampler import CohortSampler
from synthetic_citizen_lab.cohort.storage import load_cohort_definition
from synthetic_citizen_lab.experiments.context import (
    CohortArtifactNotFoundError,
    MissingPersonaColumnsError,
    MissingSampledPersonasError,
    PersonaContextLevel,
    PersonaSourceNotFoundError,
    load_persona_contexts,
)


def _write_context_fixture(path: Path) -> None:
    table = pa.table(
        {
            "uuid": pa.array(["p1", "p2", "p3"]),
            "age": pa.array([25, 45, 65], type=pa.int64()),
            "sex": pa.array(["여자", "남자", "여자"]),
            "region": pa.array(["서울", "서울", "경기"]),
            "district": pa.array(["강남구", "마포구", "수원시"]),
            "marital_status": pa.array(["미혼", "기혼", "기혼"]),
            "education_level": pa.array(["고등학교", "대학원", "중학교"]),
            "bachelors_field": pa.array(["해당없음", "공학", "해당없음"]),
            "occupation": pa.array(["자영업자", "회사원", "교사"]),
            "family_type": pa.array(["1인가구", "부부", "부부+자녀"]),
            "housing_type": pa.array(["아파트", "아파트", "단독주택"]),
            "housing_tenure": pa.array(["자가", "전세", "월세"]),
            "military_status": pa.array(["해당없음", "군필", "해당없음"]),
            "economic_activity_status": pa.array(["취업자", "취업자", "취업자"]),
            "income_bracket": pa.array(["150~250만원", "350~450만원", "250~350만원"]),
            "bmi_status": pa.array(["정상", "비만", "과체중"]),
            "blood_pressure_status": pa.array(["정상", "고혈압", "고혈압전단계"]),
            "blood_sugar_status": pa.array(["정상", "당뇨", "공복혈당장애"]),
            "waist_status": pa.array(["정상", "복부비만", "정상"]),
            "smoking_status": pa.array(["비흡연", "현재흡연", "금연"]),
            "drinking_status": pa.array(["비음주", "음주", "음주"]),
            "openness": pa.array(
                [
                    '{"t_score": 40, "label": "낮음"}',
                    '{"t_score": 55, "label": "높음"}',
                    '{"t_score": 49, "label": "보통"}',
                ]
            ),
            "conscientiousness": pa.array(['{"t_score": 50, "label": "보통"}'] * 3),
            "extraversion": pa.array(['{"t_score": 50, "label": "보통"}'] * 3),
            "agreeableness": pa.array(['{"t_score": 50, "label": "보통"}'] * 3),
            "neuroticism": pa.array(['{"t_score": 50, "label": "보통"}'] * 3),
            "detailed_persona": pa.array(["detail one", "detail two", "detail three"]),
            "persona": pa.array(["story one", "story two", "story three"]),
        }
    )
    pq.write_table(table, path)


@pytest.fixture
def sampled_cohort_dir(tmp_path: Path) -> Path:
    source_path = tmp_path / "fixture.parquet"
    output_dir = tmp_path / "outputs"
    _write_context_fixture(source_path)
    return CohortSampler(source_path).save_sample(
        CohortRequest(
            name="context fixture",
            filters=CohortFilter(),
            sampling=SamplingSpec(sample_size=3, seed=7),
        ),
        output_dir=output_dir,
    )


def test_p1_context_returns_demographic_and_socioeconomic_fields_only(
    sampled_cohort_dir: Path,
) -> None:
    contexts = load_persona_contexts(sampled_cohort_dir, PersonaContextLevel.P1)
    cohort_definition = load_cohort_definition(sampled_cohort_dir / "cohort.json")

    assert len(contexts) == 3
    assert (
        tuple(context.persona_id for context in contexts)
        == cohort_definition.persona_ids
    )

    indexed_contexts = {context.persona_id: context for context in contexts}
    assert indexed_contexts["p1"].occupation == "자영업자"
    assert indexed_contexts["p1"].income_bracket == "150~250만원"
    assert not hasattr(indexed_contexts["p1"], "bmi_status")
    assert not hasattr(indexed_contexts["p1"], "narratives")


def test_p2_context_adds_health_and_personality_without_narratives(
    sampled_cohort_dir: Path,
) -> None:
    contexts = load_persona_contexts(sampled_cohort_dir, PersonaContextLevel.P2)
    indexed_contexts = {context.persona_id: context for context in contexts}

    assert len(contexts) == 3
    assert indexed_contexts["p2"].bmi_status == "비만"
    assert indexed_contexts["p2"].blood_sugar_status == "당뇨"
    assert indexed_contexts["p2"].openness == '{"t_score": 55, "label": "높음"}'
    assert not hasattr(indexed_contexts["p2"], "narratives")


def test_p3_context_includes_ordered_narratives(sampled_cohort_dir: Path) -> None:
    contexts = load_persona_contexts(sampled_cohort_dir, PersonaContextLevel.P3)
    indexed_contexts = {context.persona_id: context for context in contexts}

    assert len(contexts) == 3
    assert tuple(
        narrative.field_name for narrative in indexed_contexts["p3"].narratives
    ) == tuple(
        column
        for column in NARRATIVE_COLUMNS
        if column in {"persona", "detailed_persona"}
    )
    assert indexed_contexts["p3"].narratives[0].text == "story three"
    assert indexed_contexts["p3"].narratives[1].text == "detail three"


def test_missing_cohort_definition_raises(tmp_path: Path) -> None:
    with pytest.raises(CohortArtifactNotFoundError, match=r"cohort\.json"):
        load_persona_contexts(tmp_path, PersonaContextLevel.P1)


def test_missing_source_file_raises(sampled_cohort_dir: Path) -> None:
    source_path = load_cohort_definition(sampled_cohort_dir / "cohort.json").source.path
    source_path.unlink()

    with pytest.raises(PersonaSourceNotFoundError):
        load_persona_contexts(sampled_cohort_dir, PersonaContextLevel.P1)


def test_missing_required_p1_column_raises(tmp_path: Path) -> None:
    source_path = tmp_path / "missing-column.parquet"
    output_dir = tmp_path / "outputs"
    table = pa.table(
        {
            "uuid": pa.array(["p1"]),
            "age": pa.array([25], type=pa.int64()),
            "sex": pa.array(["여자"]),
            "region": pa.array(["서울"]),
            "district": pa.array(["강남구"]),
            "marital_status": pa.array(["미혼"]),
            "education_level": pa.array(["고등학교"]),
            "occupation": pa.array(["자영업자"]),
            "family_type": pa.array(["1인가구"]),
            "housing_type": pa.array(["아파트"]),
            "housing_tenure": pa.array(["자가"]),
            "military_status": pa.array(["해당없음"]),
            "economic_activity_status": pa.array(["취업자"]),
            "income_bracket": pa.array(["150~250만원"]),
            "bmi_status": pa.array(["정상"]),
            "blood_pressure_status": pa.array(["정상"]),
            "blood_sugar_status": pa.array(["정상"]),
            "smoking_status": pa.array(["비흡연"]),
            "drinking_status": pa.array(["비음주"]),
        }
    )
    pq.write_table(table, source_path)
    cohort_dir = CohortSampler(source_path).save_sample(
        CohortRequest(
            name="missing column fixture",
            filters=CohortFilter(),
            sampling=SamplingSpec(sample_size=1, seed=1),
        ),
        output_dir=output_dir,
    )

    with pytest.raises(MissingPersonaColumnsError, match=r"bachelors_field"):
        load_persona_contexts(cohort_dir, PersonaContextLevel.P1)


def test_missing_sampled_persona_raises(sampled_cohort_dir: Path) -> None:
    cohort_definition_path = sampled_cohort_dir / "cohort.json"
    cohort_definition = load_cohort_definition(cohort_definition_path)
    corrupted_payload = cohort_definition.model_dump(mode="json") | {
        "persona_ids": [*cohort_definition.persona_ids, "missing-persona"],
    }
    cohort_definition_path.write_text(
        json.dumps(corrupted_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    with pytest.raises(MissingSampledPersonasError, match=r"missing-persona"):
        load_persona_contexts(sampled_cohort_dir, PersonaContextLevel.P1)
