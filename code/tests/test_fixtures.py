from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

import main
from erasecase.contracts import CaseAssessment
from erasecase.fixtures import run_fixture_review, synthetic_cases
from erasecase.models import ROOT
from erasecase.presentation import format_check, serialize_steps


def test_synthetic_cases_cover_three_finished_verdicts() -> None:
    cases = {case.case_id: case for case in synthetic_cases()}
    assert list(cases) == [
        "fixture_complete",
        "fixture_incomplete",
        "fixture_not_applicable",
    ]
    assert cases["fixture_complete"].deletion_status.value == "COMPLETE"
    assert {step.phase.value for step in cases["fixture_complete"].steps} == {"VERIFICATION"}
    assert all(step.evidence_id for step in cases["fixture_complete"].steps)
    incomplete = cases["fixture_incomplete"]
    assert [step.operation.value for step in incomplete.steps][:2] == [
        "REPORT_REMAINING_RECORD",
        "REPORT_ACTIVE_DATA_FLOW",
    ]
    assert incomplete.steps[2].operation.value == "DISABLE_DATA_FLOW"
    assert incomplete.steps[2].evidence_id == ""
    assert all(step.evidence_id == "" for step in incomplete.steps if step.phase.value != "FINDING")
    assert cases["fixture_not_applicable"].steps == ()
    encoded = json.loads(serialize_steps(incomplete.steps))
    assert list(encoded[0]) == [
        "step_no",
        "phase",
        "system_id",
        "resource_id",
        "operation",
        "state",
        "evidence_id",
    ]


def test_success_publishes_isolated_artifacts(tmp_path: Path) -> None:
    destination = tmp_path / "fixtures"
    review = run_fixture_review(destination, ROOT)
    text = "\n".join(review.lines)
    assert "FIXTURE REVIEW" in text
    assert "output.csv was not written" in text
    assert "finished verdict" in text
    csv_path = destination / "fixture_cases.csv"
    report = (destination / "fixture_review.md").read_text(encoding="utf-8")
    assert "Label: FIXTURE" in report
    assert "not evaluation predictions" in report
    with csv_path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert [row["case_id"] for row in rows] == [
        "fixture_complete",
        "fixture_incomplete",
        "fixture_not_applicable",
    ]
    for row in rows:
        CaseAssessment.model_validate(
            {
                "case_id": row["case_id"],
                "deletion_status": row["deletion_status"],
                "steps": json.loads(row["steps_json"]),
            }
        )
    assert not (ROOT / "output.csv").exists()


def test_repository_and_dataset_paths_are_rejected(tmp_path: Path) -> None:
    with pytest.raises(Exception, match="FIXTURE_INPUT"):
        run_fixture_review(ROOT / "code", ROOT)
    with pytest.raises(Exception, match="FIXTURE_INPUT"):
        run_fixture_review(ROOT / "dataset" / "review", ROOT)
    file_path = tmp_path / "notes.txt"
    file_path.write_text("x", encoding="utf-8")
    with pytest.raises(Exception, match="is a file"):
        run_fixture_review(file_path, ROOT)
    with pytest.raises(Exception, match="output.csv"):
        run_fixture_review(tmp_path / "output.csv", ROOT)


def test_failed_scenarios_keep_previous_artifacts(tmp_path: Path) -> None:
    destination = tmp_path / "fixtures"
    run_fixture_review(destination, ROOT)
    original = (destination / "fixture_cases.csv").read_bytes()
    for scenario, code, marker in (
        ("empty", 3, "FIXTURE_EMPTY"),
        ("malformed", 3, "COMPLETE permits evidence-backed verification"),
        ("budget", 4, "no provider call"),
        ("partial", 4, "previous fixture artifacts were kept"),
        ("missing-input", 2, "requires --run-dir"),
    ):
        with pytest.raises(Exception, match=marker) as caught:
            run_fixture_review(destination, ROOT, scenario)
        assert caught.value.exit_code == code
        assert (destination / "fixture_cases.csv").read_bytes() == original
        assert not (destination / ".fixture-staging").exists()


def test_cli_success_and_interrupt(tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch) -> None:
    destination = tmp_path / "fixtures"
    assert main.main(["fixtures", "--run-dir", str(destination)]) == 0
    stdout = capsys.readouterr().out
    assert "INCOMPLETE      fixture_incomplete" in stdout
    assert "NOT_APPLICABLE  fixture_not_applicable" in stdout
    assert main.run(["fixtures", "--run-dir", str(destination), "--scenario", "interrupt"]) == 130
    assert capsys.readouterr().err == "interrupted\n"
    assert (destination / "fixture_cases.csv").exists()

    def boom(argv: list[str] | None = None) -> int:
        del argv
        raise KeyboardInterrupt

    monkeypatch.setattr(main, "main", boom)
    assert main.run(["fixtures"]) == 130
    assert capsys.readouterr().err == "interrupted\n"


def test_cli_help_and_preflight_hint(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        main.main(["--help"])
    assert caught.value.code == 0
    help_text = capsys.readouterr().out
    assert "does not read evaluation requests" in help_text
    assert "write output.csv" in help_text
    assert "130" in help_text
    assert "install poppler-utils" in format_check("pdftotext", False, "missing")


def test_malformed_contract_is_the_same_validator() -> None:
    with pytest.raises(ValidationError, match="COMPLETE permits evidence-backed verification"):
        CaseAssessment.model_validate(
            {
                "case_id": "fixture_malformed",
                "deletion_status": "COMPLETE",
                "steps": [
                    {
                        "step_no": 1,
                        "phase": "FINDING",
                        "system_id": "account_service",
                        "resource_id": "fixture_bad",
                        "operation": "REPORT_REMAINING_RECORD",
                        "state": "PRESENT",
                        "evidence_id": "fixture-evidence-bad",
                    }
                ],
            }
        )
