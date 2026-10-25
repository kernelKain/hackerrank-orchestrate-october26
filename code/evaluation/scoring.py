"""Score participant-visible reference labels. Audit code does not import this module."""

from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from erasecase.audit import Auditor, open_auditor
from erasecase.contracts import CaseAssessment, DeletionRequest
from erasecase.evidence import _strong_identifiers

from .custom_cases import CustomCase, _steps, build_custom_cases
from .metrics import SuiteMetrics, combine, score_case

DATASET = Path(__file__).resolve().parents[2] / "dataset"


@dataclass(frozen=True)
class CaseScore:
    case_id: str
    expected_status: str
    actual_status: str
    sequence_match: bool
    full_row_match: bool
    missing_steps: int
    extra_steps: int
    category: str


@dataclass(frozen=True)
class PublicEvaluation:
    metrics: SuiteMetrics
    cases: tuple[CaseScore, ...]
    categories: tuple[tuple[str, int], ...]


def score_public(dataset_root: Path = DATASET, auditor: Auditor | None = None) -> PublicEvaluation:
    """Score the 32 public samples. Only this module reads sample_output.csv."""

    if auditor is None:
        auditor, _bundle = open_auditor(dataset_root)
    requests = _requests(dataset_root / "sample_deletion_requests.csv")
    expected = {
        row["case_id"]: row
        for row in csv.DictReader((dataset_root / "sample_output.csv").open(encoding="utf-8"))
    }
    subject_keys = {
        request.case_id: _subject_keys(auditor, request) for request in requests
    }
    observations = auditor.evidence.catalog.observations
    by_resource: dict[str, list] = {}
    for observation in observations:
        by_resource.setdefault(observation.resource_id, []).append(observation)
    scored: list[SuiteMetrics] = []
    cases: list[CaseScore] = []
    for request in requests:
        actual = auditor.assess(request).case
        golden_steps = json.loads(expected[request.case_id]["steps_json"])
        expected_steps = tuple(_golden_step(step) for step in golden_steps)
        actual_steps = _steps(actual)
        metrics = score_case(
            actual_status=actual.deletion_status.value,
            expected_status=expected[request.case_id]["deletion_status"],
            actual_steps=actual_steps,
            expected_steps=expected_steps,
        )
        scored.append(metrics)
        category = _category(
            actual_steps,
            expected_steps,
            golden_steps,
            subject_keys[request.case_id],
            by_resource,
            request,
        )
        cases.append(
            CaseScore(
                case_id=request.case_id,
                expected_status=expected[request.case_id]["deletion_status"],
                actual_status=actual.deletion_status.value,
                sequence_match=bool(metrics.sequence_hits),
                full_row_match=bool(metrics.full_row_hits),
                missing_steps=metrics.false_negatives,
                extra_steps=metrics.false_positives,
                category=category,
            )
        )
    counts = Counter(item.category for item in cases if not item.sequence_match)
    return PublicEvaluation(
        metrics=combine(tuple(scored)),
        cases=tuple(cases),
        categories=tuple(sorted(counts.items())),
    )


def score_custom(dataset_root: Path = DATASET) -> tuple[SuiteMetrics, tuple[CustomCase, ...]]:
    """Score fictional cases whose expected steps were written independently."""

    cases = build_custom_cases(dataset_root)
    metrics = combine(
        tuple(
            score_case(
                actual_status=case.assessment.deletion_status.value,
                expected_status=case.expected_status,
                actual_steps=_steps(case.assessment),
                expected_steps=case.expected_steps,
            )
            for case in cases
            if case.independent_expectation
        )
    )
    return metrics, cases


def _requests(path: Path) -> tuple[DeletionRequest, ...]:
    with path.open(encoding="utf-8", newline="") as handle:
        return tuple(DeletionRequest.model_validate(row) for row in csv.DictReader(handle))


def _subject_keys(auditor: Auditor, request: DeletionRequest) -> set[tuple[str, str]]:
    subjects = auditor.identity.resolve_email(request.email, known_at=request.audit_at)
    if len(subjects) != 1:
        return set()
    subject_id = next(iter(subjects))
    return {
        (fact.kind, fact.normalized_value)
        for fact in auditor.identity.for_subject(subject_id, known_at=request.audit_at)
    }


def _golden_step(step: dict[str, object]) -> tuple[object, ...]:
    return (
        step["step_no"],
        step["phase"],
        step["system_id"],
        step["resource_id"],
        step["operation"],
        step["state"],
        step["evidence_id"],
    )


def _category(
    actual_steps: tuple[tuple[object, ...], ...],
    expected_steps: tuple[tuple[object, ...], ...],
    golden_steps: list[dict[str, object]],
    keys: set[tuple[str, str]],
    by_resource: dict[str, list],
    request: DeletionRequest,
) -> str:
    if actual_steps == expected_steps:
        return "exact"
    actual_keys = {(step[2], step[3], step[4]) for step in actual_steps}
    reasons: set[str] = set()
    for step in golden_steps:
        key = (step["system_id"], step["resource_id"], step["operation"])
        if key in actual_keys:
            continue
        observations = by_resource.get(str(step["resource_id"]), [])
        timely = [
            item
            for item in observations
            if item.captured_at <= request.audit_at
            and (item.event_at is None or item.event_at <= request.audit_at)
        ]
        linked = [item for item in timely if _strong_identifiers(item.facts) & keys]
        if not observations:
            reasons.add("resource_not_in_evidence")
        elif not timely:
            reasons.add("only_after_cutoff")
        elif not linked:
            reasons.add("no_supported_identifier")
        else:
            reasons.add("linked_but_omitted")
    extra = {(step[2], step[3], step[4]) for step in actual_steps} - {
        (step["system_id"], step["resource_id"], step["operation"]) for step in golden_steps
    }
    if extra:
        reasons.add("extra_step")
    return "+".join(sorted(reasons)) or "field_mismatch"


def render_case_lines(case: CaseAssessment) -> list[str]:
    return [
        (
            f"{step.step_no}. {step.phase.value} {step.system_id} {step.resource_id} "
            f"{step.operation.value} {step.state.value} evidence={step.evidence_id or '-'}"
        )
        for step in case.steps
    ]
