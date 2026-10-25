"""Provenance, fingerprint, and publish checks for the frozen final run."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pytest

import main
from erasecase.contracts import (
    CaseAssessment,
    DeletionRequest,
    EvidenceFile,
    IdentityAuditEvent,
    OutputStep,
    SystemActivity,
)
from erasecase.final_run import evidence_fingerprint, publish_output, verify_recorded_files
from erasecase.validators import ValidationFailure, check_citation_provenance, parse_output_csv

UTC = timezone.utc


def _request(case_id: str, audit_at: datetime) -> DeletionRequest:
    return DeletionRequest(
        case_id=case_id,
        email="ada@example.test",
        requested_at=datetime(2026, 1, 1, tzinfo=UTC),
        reported_status="COMPLETE",
        reported_at=datetime(2026, 1, 2, tzinfo=UTC),
        audit_at=audit_at,
        request_text="Please delete my account.",
    )


def _step(evidence_id: str) -> OutputStep:
    return OutputStep(
        step_no=1,
        phase="VERIFICATION",
        system_id="account_service",
        resource_id="account_100",
        operation="VERIFY_RECORD_ABSENT",
        state="ABSENT",
        evidence_id=evidence_id,
    )


def test_provenance_rejects_unknown_and_future_citations() -> None:
    request = _request("case_a", datetime(2026, 1, 3, tzinfo=UTC))
    late = EvidenceFile(
        file_id="evidence_late",
        file_path="evidence/late.txt",
        origin="archive",
        captured_at=datetime(2026, 2, 1, tzinfo=UTC),
    )
    timely = EvidenceFile(
        file_id="evidence_ok",
        file_path="evidence/ok.txt",
        origin="archive",
        captured_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    activity = SystemActivity(
        activity_id="activity_1",
        event_time=datetime(2026, 1, 1, tzinfo=UTC),
        event_type="backup",
        source_system="backup_service",
        target_system="backup_service",
        resource_id="backup_1",
        reported_result="blocked",
        details="",
    )
    audit = IdentityAuditEvent(
        audit_id="audit_1",
        user_id="user_1",
        event_time=datetime(2026, 1, 1, tzinfo=UTC),
        field_name="email",
        old_value="old@example.test",
        new_value="ada@example.test",
    )
    case = CaseAssessment(case_id="case_a", deletion_status="COMPLETE", steps=(_step("missing"),))
    with pytest.raises(ValidationFailure, match="unknown evidence"):
        check_citation_provenance((case,), (request,), (timely,), (activity,), (audit,))
    late_case = case.model_copy(update={"steps": (_step("evidence_late"),)})
    with pytest.raises(ValidationFailure, match="after audit_at"):
        check_citation_provenance((late_case,), (request,), (late,), (activity,), (audit,))
    ok_case = case.model_copy(update={"steps": (_step("evidence_ok"),)})
    check_citation_provenance((ok_case,), (request,), (timely,), (activity,), (audit,))


def test_rejected_csv_does_not_replace_a_previous_submission(tmp_path: Path) -> None:
    output = tmp_path / "output.csv"
    output.write_text("KEEP\n", encoding="utf-8")
    with pytest.raises(ValidationFailure):
        parse_output_csv("case_id,deletion_status,steps_json\n", expected_ids=("case_01",))
        publish_output("SHOULD_NOT\n", output)
    assert output.read_text(encoding="utf-8") == "KEEP\n"
    publish_output("NEXT\n", output)
    assert output.read_text(encoding="utf-8") == "NEXT\n"
    assert not list(tmp_path.glob(".output.csv.*.partial"))


def test_rehash_detects_a_changed_evidence_file(tmp_path: Path) -> None:
    dataset = tmp_path / "dataset"
    target = dataset / "evidence" / "note.txt"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"alpha")
    record = {
        "evidence_id": "evidence_01",
        "file_path": "evidence/note.txt",
        "origin": "archive",
        "captured_at": "2026-01-01T00:00:00Z",
        "sha256": hashlib.sha256(b"alpha").hexdigest(),
        "byte_count": 5,
        "status": "EXTRACTED",
    }
    assert verify_recorded_files(dataset, [record]) == evidence_fingerprint([record])
    target.write_bytes(b"bravo!")
    with pytest.raises(ValidationFailure, match="fingerprint"):
        verify_recorded_files(dataset, [record])


def test_over_budget_and_missing_resume_stop(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main.main(["run", "--budget-usd", "4.01", "--run-dir", str(tmp_path / "final")]) == 2
    assert "from 0 through 4" in capsys.readouterr().err
    assert main.main(["run", "--budget-usd", "0", "--run-dir", str(tmp_path / "final"), "--resume", "missing"]) == 4
    assert "manifest" in capsys.readouterr().err
