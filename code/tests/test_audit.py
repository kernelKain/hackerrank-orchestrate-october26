"""Policy treatment, intent, ordering, and the initial public-sample evaluation."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from erasecase.audit import Auditor, UnresolvedIntent, deletion_authorized, open_auditor
from erasecase.contracts import (
    DeletionRequest,
    DeletionRule,
    DeletionStatus,
    IdentifierFact,
    Observation,
    Operation,
    Phase,
)
from erasecase.evidence import EvidenceCatalog, EvidenceIndex
from erasecase.identity import IdentityIndex, normalize_identifier
from erasecase.models import ROOT, intent_request_body
from erasecase.presentation import render_csv
from erasecase.validators import parse_output_csv

UTC = timezone.utc
DATASET = ROOT / "dataset"


def _fact(kind: str, value: str) -> IdentifierFact:
    return IdentifierFact(
        subject_id="user_1",
        kind=kind,
        normalized_value=normalize_identifier(kind, value),
        original_value=value,
        available_at=datetime(2026, 1, 1, tzinfo=UTC),
        source_id="user_1",
        source_location="test",
    )


def _observation(**overrides: object) -> Observation:
    payload: dict[str, object] = {
        "observation_id": "obs-1",
        "evidence_id": "evidence_1",
        "system_id": "account_service",
        "resource_id": "account_1",
        "captured_at": datetime(2026, 2, 1, tzinfo=UTC),
        "event_at": datetime(2026, 2, 1, tzinfo=UTC),
        "state": "ACTIVE",
        "facts": {
            "record_type": "USER_PROFILE",
            "email": "ada@example.com",
            "result": "FOUND",
            "_source_type": "evidence",
        },
    }
    payload.update(overrides)
    return Observation.model_validate(payload)


def _request(text: str, *, reported: str = "COMPLETE") -> DeletionRequest:
    return DeletionRequest(
        case_id="case_test",
        email="ada@example.com",
        requested_at=datetime(2026, 2, 2, tzinfo=UTC),
        reported_status=reported,
        reported_at=datetime(2026, 2, 3, tzinfo=UTC),
        audit_at=datetime(2026, 2, 4, tzinfo=UTC),
        request_text=text,
    )


def _auditor(*observations: Observation) -> Auditor:
    identity = IdentityIndex((_fact("email", "ada@example.com"), _fact("user_id", "user_1")))
    catalog = EvidenceCatalog(extractions=(), observations=observations, links=())
    rules = (
        DeletionRule(
            rule_id="rule_01",
            data_category="USER_PROFILE",
            condition="Always",
            required_action="DELETE",
        ),
        DeletionRule(
            rule_id="rule_15",
            data_category="ACCOUNT_TOMBSTONE",
            condition="Account is deleted",
            required_action="REDACT",
        ),
        DeletionRule(
            rule_id="rule_14",
            data_category="BACKUP_ARCHIVE",
            condition="Restore access can be blocked",
            required_action="RETAIN",
        ),
    )
    return Auditor(identity, EvidenceIndex(catalog), rules)


def test_access_request_is_not_applicable_and_ambiguous_text_stops() -> None:
    result = _auditor().assess(_request("Please export my data and keep the account."))
    assert result.case.deletion_status is DeletionStatus.NOT_APPLICABLE
    assert result.case.steps == ()
    with pytest.raises(UnresolvedIntent):
        deletion_authorized("Hello, can somebody look at this?")
    assert deletion_authorized("Hello", classifier=lambda _text: False) is False


def test_remaining_profile_plans_delete_and_records_the_contradiction() -> None:
    result = _auditor(_observation()).assess(_request("Please delete my account."))
    assert result.case.deletion_status is DeletionStatus.INCOMPLETE
    assert [step.operation for step in result.case.steps] == [
        Operation.REPORT_REMAINING_RECORD,
        Operation.DELETE_RECORD,
        Operation.VERIFY_RECORD_ABSENT,
    ]
    assert result.case.steps[0].evidence_id == "evidence_1"
    assert result.case.steps[1].evidence_id == ""
    assert result.case.steps[2].evidence_id == ""
    assert result.contradictions
    assert result.obligations[0].required_action == "DELETE"


def test_activity_claim_is_not_treated_as_proof() -> None:
    claim = _observation(
        observation_id="activity-observation:activity_1",
        evidence_id="activity_1",
        state="SUCCESS",
        facts={"email": "ada@example.com", "result": "SUCCESS", "_source_type": "activity_claim"},
    )
    result = _auditor(claim).assess(_request("Please erase this account."))
    assert result.case.deletion_status is DeletionStatus.COMPLETE
    assert result.case.steps == ()


def test_exposed_tombstone_is_redacted_before_verification() -> None:
    tombstone = _observation(
        observation_id="obs-tomb",
        system_id="identity_service",
        resource_id="tombstone_9",
        state="DELETED",
        facts={
            "record_type": "ACCOUNT_TOMBSTONE",
            "subject_reference": "user_1",
            "email": "ada@example.com",
            "account_status": "DELETED",
            "_source_type": "evidence",
        },
    )
    result = _auditor(tombstone).assess(
        _request("Remove my contact details, but a deleted-account reference may remain.")
    )
    assert result.case.steps[0].operation is Operation.REPORT_EXPOSED_PII
    assert result.case.steps[1].operation is Operation.REDACT_RECORD
    assert result.case.steps[2].operation is Operation.VERIFY_RECORD_REDACTED


def test_compliant_tombstone_and_blocked_backup_verify_without_findings() -> None:
    tombstone = _observation(
        observation_id="obs-tomb",
        system_id="identity_service",
        resource_id="tombstone_9",
        state="DELETED",
        facts={
            "record_type": "ACCOUNT_TOMBSTONE",
            "subject_reference": "user_1",
            "email": "None",
            "phone": "None",
            "email_hash": "None",
            "_source_type": "evidence",
        },
    )
    backup = _observation(
        observation_id="obs-backup",
        evidence_id="evidence_2",
        system_id="backup_service",
        resource_id="backup_9",
        state="BLOCKED",
        facts={
            "record_type": "BACKUP_ARCHIVE",
            "customer_reference": "user_1",
            "restore_allowed": False,
            "_source_type": "evidence",
        },
    )
    result = _auditor(tombstone, backup).assess(_request("Please delete my account."))
    assert result.case.deletion_status is DeletionStatus.COMPLETE
    assert [step.phase for step in result.case.steps] == [Phase.VERIFICATION, Phase.VERIFICATION]
    assert {step.operation for step in result.case.steps} == {
        Operation.VERIFY_RECORD_REDACTED,
        Operation.VERIFY_RESTORE_BLOCKED,
    }
    assert all(step.evidence_id for step in result.case.steps)


def test_later_absence_overrides_an_older_replica() -> None:
    older = _observation(
        observation_id="obs-old",
        evidence_id="evidence_old",
        event_at=datetime(2026, 2, 1, tzinfo=UTC),
        captured_at=datetime(2026, 2, 1, tzinfo=UTC),
    )
    newer = _observation(
        observation_id="obs-new",
        evidence_id="evidence_new",
        event_at=datetime(2026, 2, 3, tzinfo=UTC),
        captured_at=datetime(2026, 2, 3, tzinfo=UTC),
        state="404",
        facts={"record_type": "USER_PROFILE", "status_code": "404", "lookup_key": "ada@example.com"},
    )
    result = _auditor(older, newer).assess(_request("Please delete my account.", reported="NOT_STARTED"))
    assert result.case.deletion_status is DeletionStatus.COMPLETE
    assert result.case.steps[0].operation is Operation.VERIFY_RECORD_ABSENT
    assert result.case.steps[0].evidence_id == "evidence_new"
    assert result.contradictions


def test_older_absent_profile_lookup_does_not_add_a_second_account() -> None:
    older = _observation(
        observation_id="obs-old",
        evidence_id="evidence_old",
        resource_id="account_6523",
        event_at=datetime(2026, 3, 10, tzinfo=UTC),
        captured_at=datetime(2026, 3, 10, tzinfo=UTC),
        state="404",
        facts={
            "record_type": "USER_PROFILE",
            "http_status": "404",
            "rows": "0",
            "lookup_key": "ada@example.com",
            "_source_type": "evidence",
        },
    )
    newer = _observation(
        observation_id="obs-new",
        evidence_id="evidence_new",
        resource_id="account_4092",
        event_at=datetime(2026, 9, 15, tzinfo=UTC),
        captured_at=datetime(2026, 9, 15, tzinfo=UTC),
        state="404",
        facts={
            "record_type": "USER_PROFILE",
            "http_status": "404",
            "rows": "0",
            "lookup_key": "ada@example.com",
            "_source_type": "evidence",
        },
    )
    request = _request("Please delete my account.", reported="NOT_STARTED")
    result = _auditor(older, newer).assess(request.model_copy(update={"audit_at": datetime(2026, 10, 1, tzinfo=UTC)}))
    assert [step.resource_id for step in result.case.steps] == ["account_4092"]


def test_intent_request_uses_the_strict_schema_and_local_prompt() -> None:
    body = intent_request_body("openai/gpt-6.1-sol", "Please delete my account.")
    assert body["response_format"]["json_schema"]["strict"] is True
    assert body["response_format"]["json_schema"]["schema"]["additionalProperties"] is False
    assert "authorizes deletion" in body["messages"][0]["content"].lower()
    assert "OPENROUTER" not in json.dumps(body)


def test_public_sample_evaluation_is_structurally_valid() -> None:
    auditor, _bundle = open_auditor(DATASET)
    requests = tuple(
        DeletionRequest.model_validate(row)
        for row in csv.DictReader((DATASET / "sample_deletion_requests.csv").open(encoding="utf-8"))
    )
    expected = {
        row["case_id"]: row
        for row in csv.DictReader((DATASET / "sample_output.csv").open(encoding="utf-8"))
    }
    results = tuple(auditor.assess(request) for request in requests)
    rendered = render_csv(tuple(result.case for result in results))
    parsed = parse_output_csv(rendered, expected_ids=tuple(request.case_id for request in requests))
    assert len(parsed) == 32
    status_hits = 0
    sequence_hits = 0
    finding_evidence = 0
    finding_total = 0
    for case in parsed:
        golden = expected[case.case_id]
        status_hits += case.deletion_status.value == golden["deletion_status"]
        actual = [
            (
                step.phase.value,
                step.system_id,
                step.resource_id,
                step.operation.value,
                step.state.value,
                step.evidence_id,
            )
            for step in case.steps
        ]
        golden_steps = json.loads(golden["steps_json"])
        expected_steps = [
            (
                step["phase"],
                step["system_id"],
                step["resource_id"],
                step["operation"],
                step["state"],
                step["evidence_id"],
            )
            for step in golden_steps
        ]
        sequence_hits += actual == expected_steps
        for step in case.steps:
            if step.phase is Phase.FINDING:
                finding_total += 1
                finding_evidence += bool(step.evidence_id)
    assert finding_evidence == finding_total
    assert status_hits == 32, f"public status {status_hits}/32 sequence {sequence_hits}/32"
    # Remaining misses have no supported identifier, or their only file is after audit_at.
    assert sequence_hits >= 9, f"public sequence {sequence_hits}/32 status {status_hits}/32"
