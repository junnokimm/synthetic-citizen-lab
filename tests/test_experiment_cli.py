import json
from pathlib import Path

import pytest
from _pytest.capture import CaptureFixture

from synthetic_citizen_lab.experiment_cli import main


def test_cli_init_project_save_scenario_save_questions_and_show(
    tmp_path: Path,
    capsys: CaptureFixture[str],
) -> None:
    output_root = tmp_path / "outputs" / "experiments"

    exit_code = main(
        (
            "init-project",
            "--output-dir",
            str(output_root),
            "--project-id",
            "project_stage3",
            "--name",
            "mobility pilot",
            "--research-goal",
            "Explore synthetic persona reactions to a transport policy.",
            "--non-claim",
            "Synthetic pretest only.",
        )
    )

    assert exit_code == 0
    project_output = capsys.readouterr().out
    assert "project_path=" in project_output
    project_path = output_root / "project_stage3" / "project.json"
    assert project_path.exists()

    exit_code = main(
        (
            "save-scenario",
            "--output-dir",
            str(output_root),
            "--project-id",
            "project_stage3",
            "--scenario-id",
            "scenario_mobility_v1",
            "--title",
            "mobility support policy",
            "--variant",
            "A|Baseline support text.",
            "--variant",
            "B|Expanded support text.",
            "--variant",
            "C|Reduced support text.",
        )
    )

    assert exit_code == 0
    scenario_path = (
        output_root / "project_stage3" / "scenarios" / "scenario_mobility_v1.json"
    )
    assert scenario_path.exists()
    capsys.readouterr()

    exit_code = main(
        (
            "save-questions",
            "--output-dir",
            str(output_root),
            "--project-id",
            "project_stage3",
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
    )

    assert exit_code == 0
    question_set_path = (
        output_root
        / "project_stage3"
        / "question_sets"
        / "question_set_mobility_v1.json"
    )
    assert question_set_path.exists()
    capsys.readouterr()

    exit_code = main(
        (
            "show",
            "project",
            "--output-dir",
            str(output_root),
            "--project-id",
            "project_stage3",
        )
    )
    assert exit_code == 0
    project_payload = json.loads(capsys.readouterr().out)
    assert project_payload["project_id"] == "project_stage3"

    exit_code = main(
        (
            "show",
            "scenario",
            "--output-dir",
            str(output_root),
            "--project-id",
            "project_stage3",
            "--scenario-id",
            "scenario_mobility_v1",
        )
    )
    assert exit_code == 0
    scenario_payload = json.loads(capsys.readouterr().out)
    labels = [variant["label"] for variant in scenario_payload["variants"]]
    assert labels == ["A", "B", "C"]

    exit_code = main(
        (
            "show",
            "question-set",
            "--output-dir",
            str(output_root),
            "--project-id",
            "project_stage3",
            "--question-set-id",
            "question_set_mobility_v1",
        )
    )
    assert exit_code == 0
    question_set_payload = json.loads(capsys.readouterr().out)
    question_types = [
        question["question_type"] for question in question_set_payload["questions"]
    ]
    assert question_types == [
        "ORIGINAL",
        "SAME_QUESTION_REPEAT",
    ]


def test_cli_rejects_unsupported_question_type(
    tmp_path: Path,
    capsys: CaptureFixture[str],
) -> None:
    output_root = tmp_path / "outputs" / "experiments"

    exit_code = main(
        (
            "save-questions",
            "--output-dir",
            str(output_root),
            "--project-id",
            "project_stage3",
            "--question-set-id",
            "question_set_mobility_v1",
            "--name",
            "mobility question set",
            "--question",
            "question_main_paraphrase_v1|PARAPHRASE|같은 의미의 질문입니다.",
        )
    )

    assert exit_code == 2
    assert "Unsupported question type" in capsys.readouterr().err


def test_cli_rejects_unknown_option_typo(
    tmp_path: Path,
    capsys: CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output_root = tmp_path / "outputs" / "experiments"
    monkeypatch.chdir(tmp_path)

    exit_code = main(
        (
            "init-project",
            "--output-dr",
            str(output_root),
            "--project-id",
            "project_stage3",
            "--name",
            "mobility pilot",
            "--research-goal",
            "Explore synthetic persona reactions to a transport policy.",
            "--non-claim",
            "Synthetic pretest only.",
        )
    )

    assert exit_code == 2
    assert "Unsupported option" in capsys.readouterr().err
    assert not (tmp_path / "outputs" / "experiments" / "project_stage3").exists()


def test_cli_rejects_traversal_when_showing_project(
    tmp_path: Path,
    capsys: CaptureFixture[str],
) -> None:
    outside_project_dir = tmp_path / "outside"
    outside_project_dir.mkdir(parents=True)
    (outside_project_dir / "project.json").write_text(
        '{"project_id":"project_stage3","name":"x","research_goal":"y","non_claim":"z","created_at":"2026-07-20T12:00:00Z"}',
        encoding="utf-8",
    )

    exit_code = main(
        (
            "show",
            "project",
            "--output-dir",
            str(tmp_path / "outputs" / "experiments"),
            "--project-id",
            "../outside",
        )
    )

    assert exit_code == 2
    assert "invalid project_id" in capsys.readouterr().err


def test_cli_subcommand_help_returns_zero(capsys: CaptureFixture[str]) -> None:
    exit_code = main(("init-project", "--help"))

    assert exit_code == 0
    help_payload = json.loads(capsys.readouterr().out)
    assert help_payload["command"] == "init-project"


def test_cli_help_lists_phase_three_commands(capsys: CaptureFixture[str]) -> None:
    exit_code = main(("--help",))

    assert exit_code == 0
    help_payload = json.loads(capsys.readouterr().out)
    assert help_payload == {
        "init-project": "Create a project artifact.",
        "save-scenario": "Save one scenario definition with A/B/C-like variants.",
        "save-questions": (
            "Save one question set with ORIGINAL and "
            "SAME_QUESTION_REPEAT questions."
        ),
        "show": "Print one saved project, scenario, or question set as JSON.",
        "run": "Execute one deterministic mock experiment run.",
    }
