"""Offline metrics, fictional cases, intent coverage, and accounting guards."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from erasecase.audit import UnresolvedIntent, deletion_authorized
from erasecase.contracts import CaseAssessment, DeletionStatus, Operation, OutputStep, Phase, StepState
from erasecase.models import ProviderError, require_known_cost
from evaluation.custom_cases import build_custom_cases
from evaluation.metrics import score_case
from evaluation.scoring import score_custom, score_public

ROOT = Path(__file__).resolve().parents[2]


def test_empty_sequences_match_without_changing_step_ratios() -> None:
    metrics = score_case(
        actual_status="NOT_APPLICABLE",
        expected_status="NOT_APPLICABLE",
        actual_steps=(),
        expected_steps=(),
    )
    assert metrics.sequence_hits == 1
    assert metrics.full_row_hits == 1
    assert metrics.positional_step_slots == 0
    assert metrics.positional_step_accuracy == 1.0
    assert metrics.precision == 1.0


def test_one_sided_empty_sequence_is_a_miss() -> None:
    metrics = score_case(
        actual_status="COMPLETE",
        expected_status="COMPLETE",
        actual_steps=(("1", "VERIFICATION", "account_service", "account_1", "VERIFY_RECORD_ABSENT", "ABSENT", "evidence_01"),),
        expected_steps=(),
    )
    assert metrics.sequence_hits == 0
    assert metrics.false_positives == 1
    assert metrics.precision == 0.0


def test_local_intent_covers_previously_unresolved_phrases() -> None:
    assert deletion_authorized(
        "Solicito a exclusão permanente da conta associada a este e-mail."
    )
    assert deletion_authorized("이 이메일 주소에 연결된 계정의 영구 삭제를 요청합니다.")
    assert deletion_authorized("Please delete my account.") is True
    assert (
        deletion_authorized(
            "The mobile number on my profile is out of date. Please replace it with the new one and leave the account active."
        )
        is False
    )
    assert (
        deletion_authorized(
            "I need a copy of last year's invoices for my records. Please leave my profile and purchase history in place."
        )
        is False
    )
    assert (
        deletion_authorized(
            "Please change the email address used for this account. I want to continue using the service."
        )
        is False
    )


def test_ambiguous_text_still_stops() -> None:
    with pytest.raises(UnresolvedIntent):
        deletion_authorized("Hello, I have a question about my last order.")


def test_custom_cases_match_independent_expectations() -> None:
    metrics, cases = score_custom(ROOT / "dataset")
    assert metrics.cases == 5
    assert metrics.status_hits == metrics.cases
    assert metrics.sequence_hits == metrics.cases
    by_id = {case.case_id: case for case in cases}
    exposed = by_id["CUSTOM-03A"]
    assert exposed.assessment.deletion_status is DeletionStatus.INCOMPLETE
    assert any(
        step.operation is Operation.REPORT_EXPOSED_PII and step.resource_id == "tombstone_1003"
        for step in exposed.assessment.steps
    )
    flow = by_id["CUSTOM-03B"]
    operations = [step.operation for step in flow.assessment.steps]
    assert operations.index(Operation.DISABLE_DATA_FLOW) < operations.index(Operation.VERIFY_DATA_FLOW_DISABLED)
    assert flow.assessment.deletion_status is DeletionStatus.INCOMPLETE
    removed = by_id["CUSTOM-03E"]
    assert "audit_record_1003" not in {step.resource_id for step in removed.assessment.steps}
    assert all(step.operation is not Operation.VERIFY_RECORD_PRESENT for step in removed.assessment.steps)


def test_public_sample_metrics_are_measured() -> None:
    public = score_public(ROOT / "dataset")
    assert public.metrics.cases == 32
    assert public.metrics.status_hits == 32
    assert public.metrics.sequence_hits >= 9
    assert public.metrics.false_positives == 0
    assert "linked_but_omitted" not in {name for name, _count in public.categories}
    report = (ROOT / "code/evaluation/evaluation_report.md").read_text(encoding="utf-8")
    assert f"{public.metrics.status_hits}/32" in report
    assert f"{public.metrics.sequence_hits}/32" in report


def test_audit_sources_do_not_read_reference_labels() -> None:
    source = "\n".join(
        path.read_text(encoding="utf-8") for path in (ROOT / "code/erasecase").glob("*.py")
    )
    assert "sample_output" not in source
    assert "golden" not in source


def test_missing_provider_cost_is_not_zero() -> None:
    with pytest.raises(ProviderError):
        require_known_cost(None)


def test_finding_without_evidence_is_invalid() -> None:
    with pytest.raises(ValidationError):
        CaseAssessment(
            case_id="invalid",
            deletion_status=DeletionStatus.INCOMPLETE,
            steps=(
                OutputStep(
                    step_no=1,
                    phase=Phase.FINDING,
                    system_id="account_service",
                    resource_id="account_1",
                    operation=Operation.REPORT_REMAINING_RECORD,
                    state=StepState.PRESENT,
                    evidence_id="",
                ),
            ),
        )


def test_custom_builder_uses_only_fictional_subjects() -> None:
    cases = build_custom_cases(ROOT / "dataset")
    assert {case.case_id for case in cases} >= {"CUSTOM-01", "CUSTOM-02", "CUSTOM-03"}
    assert all(case.request.case_id.startswith("CUSTOM-") for case in cases)
