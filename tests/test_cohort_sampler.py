import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from synthetic_citizen_lab.cohort.models import (
    BigFiveFilter,
    CohortFilter,
    CohortRequest,
    SamplingSpec,
)
from synthetic_citizen_lab.cohort.options import CohortOptions
from synthetic_citizen_lab.cohort.sampler import CohortSampler
from synthetic_citizen_lab.cohort.storage import load_cohort_definition


def _write_cohort_fixture(path: Path) -> None:
    table = pa.table(
        {
            "uuid": pa.array(["p1", "p2", "p3", "p4", "p5", "p6"]),
            "first_name": pa.array(["A", "B", "C", "D", "E", "F"]),
            "street_name": pa.array(["S1", "S2", "S3", "S4", "S5", "S6"]),
            "age": pa.array([25, 45, 65, 70, 61, 45], type=pa.int64()),
            "sex": pa.array(["여자", "남자", "여자", "여자", "여자", "여자"]),
            "region": pa.array(["서울", "서울", "서울", "경기", "경기", "부산"]),
            "district": pa.array(
                ["강남구", "마포구", "강남구", "수원시", "고양시", "해운대구"]
            ),
            "marital_status": pa.array(
                ["미혼", "기혼", "기혼", "기혼", "사별", "미혼"]
            ),
            "education_level": pa.array(
                ["고등학교", "대학원", "4년제 대학교", "고등학교", "중학교", "고등학교"]
            ),
            "bachelors_field": pa.array(
                ["해당없음", "공학", "인문", "해당없음", "해당없음", "예체능"]
            ),
            "occupation": pa.array(
                ["자영업자", "회사원", "자영업자", "교사", "간호사", "자영업자"]
            ),
            "family_type": pa.array(
                ["1인가구", "부부", "부부", "부부+자녀", "1인가구", "부부"]
            ),
            "housing_type": pa.array(
                ["아파트", "아파트", "단독주택", "아파트", "연립", "아파트"]
            ),
            "housing_tenure": pa.array(
                ["자가", "전세", "자가", "월세", "자가", "전세"]
            ),
            "military_status": pa.array(
                ["해당없음", "군필", "해당없음", "해당없음", "해당없음", "해당없음"]
            ),
            "economic_activity_status": pa.array(
                ["취업자", "취업자", "비경제활동인구", "취업자", "취업자", "실업자"]
            ),
            "income_bracket": pa.array(
                [
                    "150~250만원",
                    "350~450만원",
                    "해당없음",
                    "250~350만원",
                    "85~150만원",
                    "해당없음",
                ]
            ),
            "bmi_status": pa.array(
                ["정상", "비만", "과체중", "정상", "비만", "저체중"]
            ),
            "blood_pressure_status": pa.array(
                ["정상", "고혈압", "고혈압전단계", "고혈압", "고혈압전단계", "정상"]
            ),
            "blood_sugar_status": pa.array(
                ["정상", "당뇨", "공복혈당장애", "당뇨", "정상", "정상"]
            ),
            "waist_status": pa.array(
                ["정상", "복부비만", "정상", "복부비만", "정상", "정상"]
            ),
            "smoking_status": pa.array(
                ["비흡연", "현재흡연", "비흡연", "금연", "현재흡연", "비흡연"]
            ),
            "drinking_status": pa.array(
                ["비음주", "음주", "음주", "비음주", "음주", "비음주"]
            ),
            "openness": pa.array(
                [
                    '{"t_score": 40, "label": "낮음", "description": "a"}',
                    '{"t_score": 55, "label": "높음", "description": "b"}',
                    '{"t_score": 60, "label": "높음", "description": "c"}',
                    "invalid-json",
                    '{"t_score": 49, "label": "보통", "description": "d"}',
                    '{"t_score": 70, "label": "높음", "description": "e"}',
                ]
            ),
            "conscientiousness": pa.array(['{"t_score": 50, "label": "보통"}'] * 6),
            "extraversion": pa.array(['{"t_score": 50, "label": "보통"}'] * 6),
            "agreeableness": pa.array(['{"t_score": 50, "label": "보통"}'] * 6),
            "neuroticism": pa.array(['{"t_score": 50, "label": "보통"}'] * 6),
            "persona": pa.array(["story"] * 6),
        }
    )
    pq.write_table(table, path, row_group_size=3)


@pytest.fixture
def cohort_path(tmp_path: Path) -> Path:
    path = tmp_path / "cohort.parquet"
    _write_cohort_fixture(path)
    return path


def test_empty_filter_matches_all_rows(cohort_path: Path) -> None:
    assert CohortSampler(cohort_path).matching_count(CohortFilter()) == 6


def test_age_range_filter(cohort_path: Path) -> None:
    count = CohortSampler(cohort_path).matching_count(
        CohortFilter(age_min=60, age_max=79)
    )
    assert count == 3


def test_multiple_values_within_same_field_use_or(cohort_path: Path) -> None:
    count = CohortSampler(cohort_path).matching_count(
        CohortFilter(sexes=("여자", "남자"))
    )
    assert count == 6


def test_different_fields_use_and(cohort_path: Path) -> None:
    count = CohortSampler(cohort_path).matching_count(
        CohortFilter(sexes=("여자",), regions=("서울",))
    )
    assert count == 2


def test_region_and_district_filter(cohort_path: Path) -> None:
    count = CohortSampler(cohort_path).matching_count(
        CohortFilter(regions=("서울",), districts=("강남구",))
    )
    assert count == 2


def test_invalid_district_region_combination(cohort_path: Path) -> None:
    with pytest.raises(ValueError, match="not present in selected regions"):
        CohortOptions(cohort_path).validate_region_districts(("서울",), ("수원시",))


def test_income_bracket_order_is_stable() -> None:
    assert CohortFilter.income_bracket_index("해당없음") == 0
    assert CohortFilter.income_bracket_index("1000만원이상") == 10


def test_income_not_applicable_is_separate_category(cohort_path: Path) -> None:
    count = CohortSampler(cohort_path).matching_count(
        CohortFilter(income_brackets=("해당없음",))
    )
    assert count == 2


def test_big_five_json_parsing(cohort_path: Path) -> None:
    diagnostics = CohortSampler(cohort_path).big_five_diagnostics("openness")
    assert diagnostics.parse_failure_count == 1


def test_big_five_t_score_filter(cohort_path: Path) -> None:
    filters = {"openness": BigFiveFilter(t_score_min=55, labels=("높음",))}
    count = CohortSampler(cohort_path).matching_count(
        CohortFilter(big_five_filters=filters)
    )
    assert count == 3


def test_big_five_invalid_json_is_handled(cohort_path: Path) -> None:
    filters = {"openness": BigFiveFilter(t_score_min=1)}
    count = CohortSampler(cohort_path).matching_count(
        CohortFilter(big_five_filters=filters)
    )
    assert count == 5


def test_occupation_exact_filter(cohort_path: Path) -> None:
    count = CohortSampler(cohort_path).matching_count(
        CohortFilter(occupations=("자영업자",))
    )
    assert count == 3


def test_occupation_search_filter(cohort_path: Path) -> None:
    count = CohortSampler(cohort_path).matching_count(
        CohortFilter(occupation_search="영업")
    )
    assert count == 3


def test_unknown_filter_field_is_rejected() -> None:
    with pytest.raises(ValueError, match="Big Five trait"):
        CohortFilter(big_five_filters={"unknown": BigFiveFilter(labels=("높음",))})


def test_same_seed_returns_same_persona_ids_and_order(cohort_path: Path) -> None:
    sampler = CohortSampler(cohort_path)
    filter_spec = CohortFilter(sexes=("여자",))
    spec = SamplingSpec(sample_size=3, seed=42)
    assert sampler.sample_ids(filter_spec, spec) == sampler.sample_ids(
        filter_spec, spec
    )


def test_different_seed_returns_different_sample(cohort_path: Path) -> None:
    sampler = CohortSampler(cohort_path)
    filter_spec = CohortFilter(sexes=("여자",))
    assert sampler.sample_ids(
        filter_spec, SamplingSpec(sample_size=3, seed=42)
    ) != sampler.sample_ids(filter_spec, SamplingSpec(sample_size=3, seed=43))


def test_sample_size_larger_than_matching_count_fails(cohort_path: Path) -> None:
    with pytest.raises(ValueError, match="larger than matching count"):
        CohortSampler(cohort_path).sample_ids(
            CohortFilter(regions=("부산",)), SamplingSpec(sample_size=2, seed=1)
        )


def test_zero_matching_rows_fails(cohort_path: Path) -> None:
    with pytest.raises(ValueError, match="matching count is zero"):
        CohortSampler(cohort_path).sample_ids(
            CohortFilter(regions=("제주",)), SamplingSpec(sample_size=1, seed=1)
        )


def test_export_excludes_name_and_address_fields(
    cohort_path: Path, tmp_path: Path
) -> None:
    cohort_dir = CohortSampler(cohort_path).save_sample(
        CohortRequest(
            name="fixture cohort",
            filters=CohortFilter(sexes=("여자",)),
            sampling=SamplingSpec(sample_size=2, seed=42),
        ),
        output_dir=tmp_path,
    )
    preview = (cohort_dir / "sample_preview.csv").read_text(encoding="utf-8")
    assert "first_name" not in preview
    assert "street_name" not in preview
    assert "persona" not in preview


def test_saved_metadata_contains_source_fingerprint(
    cohort_path: Path, tmp_path: Path
) -> None:
    cohort_dir = CohortSampler(cohort_path).save_sample(
        CohortRequest(
            name="fixture cohort",
            filters=CohortFilter(sexes=("여자",)),
            sampling=SamplingSpec(sample_size=2, seed=42),
        ),
        output_dir=tmp_path,
    )
    metadata = json.loads((cohort_dir / "cohort.json").read_text(encoding="utf-8"))
    loaded = load_cohort_definition(cohort_dir / "cohort.json")
    assert metadata["source"]["sha256"]
    assert loaded.persona_ids == tuple(metadata["persona_ids"])
