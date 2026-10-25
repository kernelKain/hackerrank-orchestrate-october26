"""Structural checks for assessments and serialized submission rows."""

from __future__ import annotations

import csv
import io
import json

from .contracts import (
    CaseAssessment,
    DeletionRequest,
    EvidenceFile,
    IdentityAuditEvent,
    OutputStep,
    SystemActivity,
)
from .presentation import STEP_KEY_ORDER


class ValidationFailure(ValueError):
    """An assessment or CSV row violates the submission contract."""


def require_unique_sorted(case_ids: tuple[str, ...]) -> None:
    if list(case_ids) != sorted(case_ids):
        raise ValidationFailure("case ids must be sorted")
    if len(case_ids) != len(set(case_ids)):
        raise ValidationFailure("case ids must be unique")


def parse_steps(payload: str) -> tuple[OutputStep, ...]:
    try:
        raw = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ValidationFailure("steps_json is not valid JSON") from exc
    if not isinstance(raw, list):
        raise ValidationFailure("steps_json must be an array")
    steps: list[OutputStep] = []
    for item in raw:
        if not isinstance(item, dict) or set(item) != set(STEP_KEY_ORDER):
            raise ValidationFailure("a step must contain exactly the seven required fields")
        steps.append(OutputStep.model_validate(item))
    return tuple(steps)


def parse_output_csv(text: str, *, expected_ids: tuple[str, ...] | None = None) -> tuple[CaseAssessment, ...]:
    """Parse a candidate submission and reject contract violations."""

    reader = csv.DictReader(io.StringIO(text))
    if tuple(reader.fieldnames or ()) != ("case_id", "deletion_status", "steps_json"):
        raise ValidationFailure("output header must be case_id,deletion_status,steps_json")
    cases: list[CaseAssessment] = []
    for row in reader:
        steps = parse_steps(row["steps_json"])
        cases.append(
            CaseAssessment(
                case_id=row["case_id"],
                deletion_status=row["deletion_status"],
                steps=steps,
            )
        )
    ids = tuple(case.case_id for case in cases)
    require_unique_sorted(ids)
    if expected_ids is not None and ids != tuple(sorted(expected_ids)):
        raise ValidationFailure("output rows must match the requested case ids")
    return tuple(cases)


def check_citation_provenance(
    cases: tuple[CaseAssessment, ...],
    requests: tuple[DeletionRequest, ...],
    evidence_files: tuple[EvidenceFile, ...],
    activities: tuple[SystemActivity, ...],
    audits: tuple[IdentityAuditEvent, ...],
) -> None:
    """Reject citations that are missing or available only after the case cutoff."""

    by_case = {item.case_id: item for item in requests}
    available_at = {item.file_id: item.captured_at for item in evidence_files}
    available_at.update({item.activity_id: item.event_time for item in activities})
    available_at.update({item.audit_id: item.event_time for item in audits})
    for case in cases:
        request = by_case.get(case.case_id)
        if request is None:
            raise ValidationFailure(f"{case.case_id} is not an evaluation request")
        for step in case.steps:
            if not step.evidence_id:
                continue
            captured = available_at.get(step.evidence_id)
            if captured is None:
                raise ValidationFailure(f"{case.case_id} cites unknown evidence {step.evidence_id}")
            if captured > request.audit_at:
                raise ValidationFailure(f"{case.case_id} cites {step.evidence_id} after audit_at")
