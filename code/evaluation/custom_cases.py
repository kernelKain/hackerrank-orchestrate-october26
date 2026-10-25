"""Fictional cases exercised through the same auditor as participant data."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone

from erasecase.audit import Auditor
from erasecase.contracts import (
    CaseAssessment,
    DeletionRequest,
    DeletionRule,
    EvidenceExtraction,
    ExtractionStatus,
    IdentifierFact,
    Observation,
)
from erasecase.evidence import EvidenceCatalog, EvidenceIndex
from erasecase.identity import IdentityIndex, normalize_identifier
from erasecase.ingest import load_dataset
from erasecase.models import ROOT

UTC = timezone.utc
T0 = datetime(2026, 1, 1, tzinfo=UTC)
T_PRIMARY = datetime(2026, 7, 1, tzinfo=UTC)
T_REPLICA = datetime(2026, 8, 1, tzinfo=UTC)
T_LATER = datetime(2026, 10, 1, tzinfo=UTC)
REQUESTED = datetime(2026, 8, 15, tzinfo=UTC)
REPORTED = datetime(2026, 8, 20, tzinfo=UTC)
AUDIT = datetime(2026, 9, 1, tzinfo=UTC)


@dataclass(frozen=True)
class CustomCase:
    case_id: str
    summary: str
    request: DeletionRequest
    assessment: CaseAssessment
    expected_status: str
    expected_steps: tuple[tuple[object, ...], ...]
    rationale: str
    independent_expectation: bool = True


def build_custom_cases(dataset_root=ROOT / "dataset") -> tuple[CustomCase, ...]:
    """Return the required scenarios and their focused mutations."""

    rules = load_dataset(dataset_root).rules
    return (
        _replica_case(rules),
        _export_case(rules),
        _compliant_case(rules),
        _exposed_tombstone_case(rules),
        _reactivated_flow_case(rules),
        _later_cleanup_case(rules),
        _unlinked_analytics_case(rules),
        _removed_retention_case(rules),
    )


def _replica_case(rules: tuple[DeletionRule, ...]) -> CustomCase:
    subject = "user_custom_01"
    historical = "old.user@example.com"
    current = "current.user@example.com"
    request = _request(
        "CUSTOM-01",
        historical,
        "Please erase the account that used this older email address.",
    )
    auditor = _auditor(
        rules,
        (
            _fact(subject, "user_id", subject),
            _fact(subject, "email", historical, valid_to=datetime(2026, 6, 1, tzinfo=UTC)),
            _fact(subject, "email", current, valid_from=datetime(2026, 6, 1, tzinfo=UTC)),
            _fact(subject, "name", "Nora Example"),
            _fact("user_decoy", "user_id", "user_decoy"),
            _fact("user_decoy", "email", "decoy.user@example.com"),
            _fact("user_decoy", "name", "Nora Example"),
        ),
        (
            _observation(
                "custom_primary",
                "account_service",
                "account_1001",
                T_PRIMARY,
                "404",
                {"lookup_key": historical, "rows": "0", "http_status": "404", "record_type": "USER_PROFILE"},
            ),
            _observation(
                "custom_replica",
                "account_service",
                "account_1001",
                T_REPLICA,
                "ACTIVE",
                {"email": historical, "rows": "1", "record_type": "USER_PROFILE"},
            ),
            _observation(
                "custom_later",
                "account_service",
                "account_1001",
                T_LATER,
                "404",
                {"email": historical, "rows": "0", "http_status": "404", "record_type": "USER_PROFILE"},
            ),
            _observation(
                "custom_decoy",
                "account_service",
                "account_1002",
                T_REPLICA,
                "ACTIVE",
                {"email": "decoy.user@example.com", "name": "Nora Example", "record_type": "USER_PROFILE"},
            ),
        ),
    )
    return _finish(
        "CUSTOM-01",
        "Historical email, clean primary, surviving replica, later cleanup, same-name decoy.",
        request,
        auditor,
        "INCOMPLETE",
        (
            (1, "FINDING", "account_service", "account_1001", "REPORT_REMAINING_RECORD", "PRESENT", "custom_replica"),
            (2, "REMEDIATION", "account_service", "account_1001", "DELETE_RECORD", "ABSENT", ""),
            (3, "VERIFICATION", "account_service", "account_1001", "VERIFY_RECORD_ABSENT", "ABSENT", ""),
        ),
        "Only the timely replica copy is a supported violation. The later cleanup and the decoy stay out.",
    )


def _export_case(rules: tuple[DeletionRule, ...]) -> CustomCase:
    request = _request(
        "CUSTOM-02",
        "export.user@example.com",
        "Je souhaite exporter mes données et conserver mon compte. Please send a copy of my data.",
    )
    auditor = _auditor(
        rules,
        (
            _fact("user_custom_02", "user_id", "user_custom_02"),
            _fact("user_custom_02", "email", "export.user@example.com"),
        ),
        (
            _observation(
                "custom_export_profile",
                "account_service",
                "account_1003",
                T_REPLICA,
                "ACTIVE",
                {"email": "export.user@example.com", "record_type": "USER_PROFILE"},
            ),
        ),
    )
    return _finish(
        "CUSTOM-02",
        "Multilingual export request that explicitly keeps the account.",
        request,
        auditor,
        "NOT_APPLICABLE",
        (),
        "An export-and-keep request produces no deletion steps, even when a profile is present.",
    )


def _compliant_case(rules: tuple[DeletionRule, ...]) -> CustomCase:
    return _finish(
        "CUSTOM-03",
        "Compliant tombstone, retention, redaction, anonymization, disabled flow, and blocked restore.",
        _request("CUSTOM-03", "done.user@example.com", "Please delete my account and personal data."),
        _compliant_auditor(rules, exposed=False, flow_enabled=False, audit_rows="1"),
        "COMPLETE",
        (
            (1, "VERIFICATION", "security_service", "audit_record_1003", "VERIFY_RECORD_PRESENT", "PRESENT", "custom_audit"),
            (2, "VERIFICATION", "account_service", "tombstone_1003", "VERIFY_RECORD_REDACTED", "REDACTED", "custom_tombstone"),
            (3, "VERIFICATION", "analytics_platform", "analytics_1003", "VERIFY_RECORD_ANONYMIZED", "ANONYMIZED", "custom_analytics_done"),
            (4, "VERIFICATION", "integration_service", "data_flow_1003", "VERIFY_DATA_FLOW_DISABLED", "DISABLED", "custom_flow"),
            (5, "VERIFICATION", "backup_service", "backup_1003", "VERIFY_RESTORE_BLOCKED", "BLOCKED", "custom_backup"),
        ),
        "Every linked obligation is already in the required state, so the plan is verification only.",
    )


def _exposed_tombstone_case(rules: tuple[DeletionRule, ...]) -> CustomCase:
    assessment = _compliant_auditor(rules, exposed=True, flow_enabled=False, audit_rows="1").assess(
        _request("CUSTOM-03A", "done.user@example.com", "Please delete my account and personal data.")
    )
    return CustomCase(
        case_id="CUSTOM-03A",
        summary="Tombstone still exposes an email address.",
        request=_request("CUSTOM-03A", "done.user@example.com", "Please delete my account and personal data."),
        assessment=assessment.case,
        expected_status="INCOMPLETE",
        expected_steps=_steps(assessment.case),
        rationale="Exposed tombstone identifiers become a redaction finding before future verification.",
        independent_expectation=False,
    )


def _reactivated_flow_case(rules: tuple[DeletionRule, ...]) -> CustomCase:
    assessment = _compliant_auditor(rules, exposed=False, flow_enabled=True, audit_rows="1").assess(
        _request("CUSTOM-03B", "done.user@example.com", "Please delete my account and personal data.")
    )
    return CustomCase(
        case_id="CUSTOM-03B",
        summary="A previously stopped connector is enabled again.",
        request=_request("CUSTOM-03B", "done.user@example.com", "Please delete my account and personal data."),
        assessment=assessment.case,
        expected_status="INCOMPLETE",
        expected_steps=_steps(assessment.case),
        rationale="An enabled flow is reported and disabled before dependent record changes.",
        independent_expectation=False,
    )


def _later_cleanup_case(rules: tuple[DeletionRule, ...]) -> CustomCase:
    """Moving the surviving replica past the cutoff removes that violation."""

    subject_email = "old.user@example.com"
    auditor = _auditor(
        rules,
        (
            _fact("user_custom_01", "user_id", "user_custom_01"),
            _fact("user_custom_01", "email", subject_email),
        ),
        (
            _observation(
                "custom_primary",
                "account_service",
                "account_1001",
                T_PRIMARY,
                "404",
                {"lookup_key": subject_email, "rows": "0", "http_status": "404", "record_type": "USER_PROFILE"},
            ),
            _observation(
                "custom_replica",
                "account_service",
                "account_1001",
                T_LATER,
                "ACTIVE",
                {"email": subject_email, "rows": "1", "record_type": "USER_PROFILE"},
            ),
        ),
    )
    return _finish(
        "CUSTOM-03C",
        "The replica capture moves to after audit_at.",
        _request("CUSTOM-03C", subject_email, "Please erase the account that used this older email address."),
        auditor,
        "COMPLETE",
        (
            (1, "VERIFICATION", "account_service", "account_1001", "VERIFY_RECORD_ABSENT", "ABSENT", "custom_primary"),
        ),
        "Evidence captured after the cutoff cannot recreate a violation or change a timely absence.",
    )


def _unlinked_analytics_case(rules: tuple[DeletionRule, ...]) -> CustomCase:
    auditor = _auditor(
        rules,
        (
            _fact("user_custom_04", "user_id", "user_custom_04"),
            _fact("user_custom_04", "email", "linked.user@example.com"),
        ),
        (
            _observation(
                "custom_linked_account",
                "account_service",
                "account_1004",
                T_REPLICA,
                "404",
                {"lookup_key": "linked.user@example.com", "rows": "0", "http_status": "404", "record_type": "USER_PROFILE"},
            ),
            _observation(
                "custom_null_analytics",
                "analytics_platform",
                "analytics_9999",
                T_REPLICA,
                "PRESENT",
                {
                    "email": "null",
                    "customer_reference": "null",
                    "email_hash": "null",
                    "trace_id": "trace-unlinked",
                    "record_type": "ANALYTICS_PROFILE",
                },
            ),
        ),
    )
    return _finish(
        "CUSTOM-04",
        "A null-identifier analytics row shares the catalog but not the subject.",
        _request("CUSTOM-04", "linked.user@example.com", "Please delete my personal data."),
        auditor,
        "COMPLETE",
        (
            (1, "VERIFICATION", "account_service", "account_1004", "VERIFY_RECORD_ABSENT", "ABSENT", "custom_linked_account"),
        ),
        "An anonymized row is not assigned to a subject without a supported identifier or a single-subject trace.",
    )


def _removed_retention_case(rules: tuple[DeletionRule, ...]) -> CustomCase:
    request = _request("CUSTOM-03E", "done.user@example.com", "Please delete my account and personal data.")
    assessment = _compliant_auditor(rules, exposed=False, flow_enabled=False, audit_rows="0").assess(request)
    resource_ids = {step.resource_id for step in assessment.case.steps}
    if "audit_record_1003" in resource_ids:
        raise RuntimeError("an explicitly absent retained record was reported as present")
    return CustomCase(
        case_id="CUSTOM-03E",
        summary="The linked security audit lookup returns zero rows.",
        request=_request("CUSTOM-03E", "done.user@example.com", "Please delete my account and personal data."),
        assessment=assessment.case,
        expected_status=assessment.case.deletion_status.value,
        expected_steps=_steps(assessment.case),
        independent_expectation=False,
        rationale=(
            "Explicit absence is not rewritten as a present retained record. "
            "The allowed operations do not include restoring a retained record, "
            "so this lookup is omitted rather than given a fabricated finding."
        ),
    )


def _compliant_auditor(
    rules: tuple[DeletionRule, ...], *, exposed: bool, flow_enabled: bool, audit_rows: str
) -> Auditor:
    email = "done.user@example.com"
    tombstone_facts: dict[str, object] = {"user_id": "user_9003", "record_type": "ACCOUNT_TOMBSTONE"}
    if exposed:
        tombstone_facts["email"] = email
    return _auditor(
        rules,
        (
            _fact("user_9003", "user_id", "user_9003"),
            _fact("user_9003", "email", email),
        ),
        (
            _observation(
                "custom_tombstone",
                "account_service",
                "tombstone_1003",
                T_REPLICA,
                "PRESENT",
                tombstone_facts,
            ),
            _observation(
                "custom_audit",
                "security_service",
                "audit_record_1003",
                T_REPLICA,
                "PRESENT",
                {
                    "subject_reference": "user_9003",
                    "rows": audit_rows,
                    "record_type": "SECURITY_AUDIT_LOG",
                },
            ),
            _observation(
                "custom_analytics_start",
                "analytics_platform",
                "analytics_1003",
                T_PRIMARY,
                "PRESENT",
                {
                    "lookup_key": email,
                    "trace_id": "trace-custom-03",
                    "event": "analytics_profile_read_started",
                    "record_type": "ANALYTICS_PROFILE",
                },
            ),
            _observation(
                "custom_analytics_done",
                "analytics_platform",
                "analytics_1003",
                T_REPLICA,
                "PRESENT",
                {
                    "email": "null",
                    "customer_reference": "null",
                    "email_hash": "null",
                    "trace_id": "trace-custom-03",
                    "event": "analytics_profile_read_completed",
                    "record_type": "ANALYTICS_PROFILE",
                },
            ),
            _observation(
                "custom_flow",
                "integration_service",
                "data_flow_1003",
                T_REPLICA,
                "DISABLED" if not flow_enabled else "ACTIVE",
                {
                    "lookup_key": email,
                    "enabled": flow_enabled,
                    "record_type": "DATA_FLOW",
                },
            ),
            _observation(
                "custom_backup",
                "backup_service",
                "backup_1003",
                T_REPLICA,
                "BLOCKED",
                {
                    "customer_reference": "user_9003",
                    "restore_allowed": False,
                    "record_type": "BACKUP_ARCHIVE",
                },
            ),
        ),
    )


def _finish(
    case_id: str,
    summary: str,
    request: DeletionRequest,
    auditor: Auditor,
    expected_status: str,
    expected_steps: tuple[tuple[object, ...], ...],
    rationale: str,
) -> CustomCase:
    assessment = auditor.assess(request).case
    return CustomCase(
        case_id=case_id,
        summary=summary,
        request=request,
        assessment=assessment,
        expected_status=expected_status,
        expected_steps=expected_steps,
        rationale=rationale,
    )


def _request(case_id: str, email: str, text: str) -> DeletionRequest:
    return DeletionRequest(
        case_id=case_id,
        email=email,
        requested_at=REQUESTED,
        reported_status="COMPLETE",
        reported_at=REPORTED,
        audit_at=AUDIT,
        request_text=text,
    )


def _fact(subject: str, kind: str, value: str, **times: datetime) -> IdentifierFact:
    return IdentifierFact(
        subject_id=subject,
        kind=kind,
        normalized_value=normalize_identifier(kind, value),
        original_value=value,
        source_id=f"{subject}:{kind}:{value}",
        available_at=T0,
        valid_from=times.get("valid_from"),
        valid_to=times.get("valid_to"),
    )


def _observation(
    evidence_id: str,
    system_id: str,
    resource_id: str,
    captured_at: datetime,
    state: str,
    facts: dict[str, object],
) -> Observation:
    return Observation(
        observation_id=f"{evidence_id}:{resource_id}",
        evidence_id=evidence_id,
        system_id=system_id,
        resource_id=resource_id,
        captured_at=captured_at,
        event_at=captured_at,
        state=state,
        facts={**facts, "_source_type": "evidence"},
        source_location=f"custom:{evidence_id}",
    )


def _auditor(
    rules: tuple[DeletionRule, ...],
    facts: tuple[IdentifierFact, ...],
    observations: tuple[Observation, ...],
) -> Auditor:
    extractions = tuple(_extraction(item.evidence_id, item.captured_at, item.system_id) for item in observations)
    catalog = EvidenceCatalog(extractions=extractions, observations=observations, links=())
    return Auditor(IdentityIndex(facts), EvidenceIndex(catalog), rules)


def _extraction(evidence_id: str, captured_at: datetime, origin: str) -> EvidenceExtraction:
    digest = hashlib.sha256(evidence_id.encode()).hexdigest()
    return EvidenceExtraction(
        evidence_id=evidence_id,
        file_path=f"custom/{evidence_id}.json",
        origin=origin,
        captured_at=captured_at,
        media_type="application/json",
        sha256=digest,
        byte_count=len(evidence_id),
        status=ExtractionStatus.EXTRACTED,
        observation_count=1,
    )


def _steps(case: CaseAssessment) -> tuple[tuple[object, ...], ...]:
    return tuple(
        (
            step.step_no,
            step.phase.value,
            step.system_id,
            step.resource_id,
            step.operation.value,
            step.state.value,
            step.evidence_id,
        )
        for step in case.steps
    )
