from pathlib import Path

import pytest
from tests.experiment_fixtures import (
    build_comparison_record,
    build_follow_up_record,
    build_project_record,
    build_question_set_record,
    build_response_records,
    build_run_record,
    build_scenario_record,
)

from synthetic_citizen_lab.experiments.storage import (
    load_comparison_records,
    load_follow_up_record,
    load_project_record,
    load_question_set_record,
    load_response_records,
    load_run_record,
    load_scenario_record,
    write_comparison_records,
    write_follow_up_record,
    write_project_record,
    write_question_set_record,
    write_response_records,
    write_run_record,
    write_scenario_record,
)


def _output_root(tmp_path: Path) -> Path:
    return tmp_path / "outputs" / "experiments"


def test_storage_writes_and_loads_canonical_layout(tmp_path: Path) -> None:
    output_root = _output_root(tmp_path)

    project_path = write_project_record(output_root, build_project_record())
    scenario_path = write_scenario_record(output_root, build_scenario_record())
    question_set_path = write_question_set_record(
        output_root,
        build_question_set_record(),
    )
    run_path = write_run_record(output_root, build_run_record())
    responses_path = write_response_records(
        output_root,
        project_id="project_stage2",
        run_id="run_20260720_001",
        responses=build_response_records(),
    )
    comparisons_path = write_comparison_records(
        output_root,
        project_id="project_stage2",
        run_id="run_20260720_001",
        file_name="repeat_stability.json",
        comparisons=(build_comparison_record(),),
    )
    follow_up_path = write_follow_up_record(output_root, build_follow_up_record())

    assert project_path == output_root / "project_stage2" / "project.json"
    assert scenario_path == (
        output_root / "project_stage2" / "scenarios" / "scenario_healthcare_v1.json"
    )
    assert question_set_path == (
        output_root
        / "project_stage2"
        / "question_sets"
        / "question_set_main_v1.json"
    )
    assert run_path == (
        output_root / "project_stage2" / "runs" / "run_20260720_001" / "run.json"
    )
    assert responses_path == (
        output_root
        / "project_stage2"
        / "runs"
        / "run_20260720_001"
        / "responses.jsonl"
    )
    assert comparisons_path == (
        output_root
        / "project_stage2"
        / "runs"
        / "run_20260720_001"
        / "comparisons"
        / "repeat_stability.json"
    )
    assert follow_up_path == (
        output_root
        / "project_stage2"
        / "runs"
        / "run_20260720_001"
        / "follow_ups"
        / "follow_up_001.json"
    )

    assert load_project_record(project_path) == build_project_record()
    assert load_scenario_record(scenario_path) == build_scenario_record()
    assert load_question_set_record(question_set_path) == build_question_set_record()
    assert load_run_record(run_path) == build_run_record()
    assert load_response_records(responses_path) == build_response_records()
    assert load_comparison_records(comparisons_path) == (build_comparison_record(),)
    assert load_follow_up_record(follow_up_path) == build_follow_up_record()


def test_storage_rejects_path_traversal_and_inconsistent_ids(tmp_path: Path) -> None:
    output_root = _output_root(tmp_path)

    with pytest.raises(ValueError, match="project_id"):
        write_response_records(
            output_root,
            project_id="../escape",
            run_id="run_20260720_001",
            responses=build_response_records(),
        )

    with pytest.raises(ValueError, match="run_id"):
        write_response_records(
            output_root,
            project_id="project_stage2",
            run_id="../escape",
            responses=build_response_records(),
        )

    with pytest.raises(ValueError, match="file_name"):
        write_comparison_records(
            output_root,
            project_id="project_stage2",
            run_id="run_20260720_001",
            file_name="../repeat_stability.json",
            comparisons=(build_comparison_record(),),
        )

    mismatched_response = build_response_records()[0].model_copy(
        update={"project_id": "project_other"}
    )
    with pytest.raises(ValueError, match="response project_id"):
        write_response_records(
            output_root,
            project_id="project_stage2",
            run_id="run_20260720_001",
            responses=(mismatched_response,),
        )

    mismatched_comparison = build_comparison_record().model_copy(
        update={"run_id": "run_20260720_other"}
    )
    with pytest.raises(ValueError, match="comparison run_id"):
        write_comparison_records(
            output_root,
            project_id="project_stage2",
            run_id="run_20260720_001",
            file_name="repeat_stability.json",
            comparisons=(mismatched_comparison,),
        )
