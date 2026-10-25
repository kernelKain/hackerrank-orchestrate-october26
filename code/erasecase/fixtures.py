"""Synthetic fixture review, isolated from evaluation predictions."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from erasecase.contracts import CaseAssessment, OutputStep
from erasecase.presentation import CommandFailure, render_case_lines, render_csv

FIXTURE_LABEL = "FIXTURE"
SCENARIOS = (
    "success",
    "empty",
    "malformed",
    "budget",
    "partial",
    "missing-input",
    "interrupt",
)
PUBLISHED_FILES = ("fixture_cases.csv", "fixture_review.md")


@dataclass(frozen=True)
class FixtureReview:
    lines: tuple[str, ...]
    run_dir: Path


def prepare_run_dir(run_dir: Path, root: Path) -> Path:
    if not str(run_dir).strip():
        raise CommandFailure(
            2,
            "FIXTURE_INPUT",
            "fixture review requires --run-dir outside the repository root and dataset/",
        )
    resolved = run_dir.expanduser().resolve()
    root_resolved = root.resolve()
    dataset = (root_resolved / "dataset").resolve()
    runs = root_resolved / "runs"
    inside_repo = resolved == root_resolved or root_resolved in resolved.parents
    outside_runs = inside_repo and resolved != runs and runs not in resolved.parents
    blocked = (
        resolved == root_resolved
        or resolved.name == "output.csv"
        or resolved == dataset
        or dataset in resolved.parents
        or resolved in root_resolved.parents
        or outside_runs
    )
    if blocked:
        raise CommandFailure(
            2,
            "FIXTURE_INPUT",
            f"{resolved} is not an isolated fixture directory; "
            "use a path under runs/ or outside the repository, never dataset/ or output.csv",
        )
    if resolved.exists() and not resolved.is_dir():
        raise CommandFailure(
            2,
            "FIXTURE_INPUT",
            f"{resolved} is a file; pass a directory such as runs/fixtures",
        )
    return resolved


def synthetic_cases() -> tuple[CaseAssessment, ...]:
    """Original labeled examples. Evidence IDs are synthetic, not dataset file IDs."""

    complete = CaseAssessment(
        case_id="fixture_complete",
        deletion_status="COMPLETE",
        steps=(
            OutputStep(
                step_no=1,
                phase="VERIFICATION",
                system_id="account_service",
                resource_id="fixture_account_complete",
                operation="VERIFY_RECORD_REDACTED",
                state="REDACTED",
                evidence_id="fixture-evidence-complete-tombstone",
            ),
            OutputStep(
                step_no=2,
                phase="VERIFICATION",
                system_id="security_service",
                resource_id="fixture_audit_complete",
                operation="VERIFY_RECORD_PRESENT",
                state="PRESENT",
                evidence_id="fixture-evidence-complete-retention",
            ),
        ),
    )
    incomplete = CaseAssessment(
        case_id="fixture_incomplete",
        deletion_status="INCOMPLETE",
        steps=(
            OutputStep(
                step_no=1,
                phase="FINDING",
                system_id="replica_service",
                resource_id="fixture_replica_incomplete",
                operation="REPORT_REMAINING_RECORD",
                state="PRESENT",
                evidence_id="fixture-evidence-incomplete-replica",
            ),
            OutputStep(
                step_no=2,
                phase="FINDING",
                system_id="integration_service",
                resource_id="fixture_sync_incomplete",
                operation="REPORT_ACTIVE_DATA_FLOW",
                state="ACTIVE",
                evidence_id="fixture-evidence-incomplete-sync",
            ),
            OutputStep(
                step_no=3,
                phase="REMEDIATION",
                system_id="integration_service",
                resource_id="fixture_sync_incomplete",
                operation="DISABLE_DATA_FLOW",
                state="DISABLED",
                evidence_id="",
            ),
            OutputStep(
                step_no=4,
                phase="REMEDIATION",
                system_id="replica_service",
                resource_id="fixture_replica_incomplete",
                operation="DELETE_RECORD",
                state="ABSENT",
                evidence_id="",
            ),
            OutputStep(
                step_no=5,
                phase="VERIFICATION",
                system_id="integration_service",
                resource_id="fixture_sync_incomplete",
                operation="VERIFY_DATA_FLOW_DISABLED",
                state="DISABLED",
                evidence_id="",
            ),
            OutputStep(
                step_no=6,
                phase="VERIFICATION",
                system_id="replica_service",
                resource_id="fixture_replica_incomplete",
                operation="VERIFY_RECORD_ABSENT",
                state="ABSENT",
                evidence_id="",
            ),
        ),
    )
    not_applicable = CaseAssessment(
        case_id="fixture_not_applicable",
        deletion_status="NOT_APPLICABLE",
        steps=(),
    )
    return tuple(sorted((complete, incomplete, not_applicable), key=lambda item: item.case_id))


def render_report(cases: tuple[CaseAssessment, ...], run_dir: Path) -> str:
    summaries = {
        "fixture_complete": (
            "Synthetic compliant tombstone and retained audit record. "
            "Evidence IDs are fixture labels, not dataset file IDs."
        ),
        "fixture_incomplete": (
            "Finished INCOMPLETE verdict: a synthetic replica remains and a sync can recreate it. "
            "Disable the flow before deleting the replica. This is not a failed command."
        ),
        "fixture_not_applicable": (
            "Synthetic export request that keeps the account. No deletion steps are produced."
        ),
    }
    sections = ["# EraseCase fixture review", "", f"Label: {FIXTURE_LABEL}", "Provider calls: 0", f"Run directory: {run_dir}", ""]
    sections.append("These cases are synthetic. They are not evaluation predictions, and this command does not write output.csv.")
    sections.append("")
    for case in cases:
        sections.append(f"## {case.deletion_status.value} — {case.case_id}")
        sections.append("")
        sections.extend(render_case_lines(case, summaries[case.case_id]))
        sections.append("")
    sections.extend(
        [
            "## Failure and recovery",
            "",
            "A failed scenario prints a specific code on stderr and leaves any previous fixture files in place.",
            "Ctrl+C prints `interrupted` on stderr and exits 130. A slow fixture review keeps the last progress line until publication finishes.",
            "",
            "| Scenario | Exit | Code | What it shows |",
            "| --- | --- | --- | --- |",
            "| success | 0 | — | Three finished verdicts, published only after validation |",
            "| empty | 3 | FIXTURE_EMPTY | An empty catalog is not a successful review |",
            "| malformed | 3 | FIXTURE_MALFORMED | A contract violation is rejected before publication |",
            "| budget | 4 | FIXTURE_BUDGET | A simulated budget stop with no provider call and no charge |",
            "| partial | 4 | FIXTURE_PARTIAL | A simulated crash before replacement keeps the previous files |",
            "| missing-input | 2 | FIXTURE_INPUT | Usage failure; no fixture files are published |",
            "| interrupt | 130 | — | Same handler as Ctrl+C: stderr `interrupted`, previous files kept |",
            "",
            "Rerun `fixtures --run-dir <directory>` after a failed scenario to replace artifacts only when validation succeeds.",
            "",
        ]
    )
    return "\n".join(sections)


def publish(run_dir: Path, csv_text: str, report_text: str, *, fail_before_replace: bool) -> None:
    staging = run_dir / ".fixture-staging"
    if staging.exists():
        shutil.rmtree(staging)
    run_dir.mkdir(parents=True, exist_ok=True)
    staging.mkdir()
    try:
        (staging / PUBLISHED_FILES[0]).write_text(csv_text, encoding="utf-8", newline="\n")
        (staging / PUBLISHED_FILES[1]).write_text(report_text, encoding="utf-8", newline="\n")
        if fail_before_replace:
            raise CommandFailure(
                4,
                "FIXTURE_PARTIAL",
                "simulated partial write stopped before replacement; previous fixture artifacts were kept",
            )
        for name in PUBLISHED_FILES:
            os.replace(staging / name, run_dir / name)
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def _scenario_failure(scenario: str) -> CommandFailure | None:
    if scenario == "empty":
        return CommandFailure(
            3,
            "FIXTURE_EMPTY",
            "fixture catalog is empty; refusing to publish a blank review",
        )
    if scenario == "malformed":
        try:
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
        except ValidationError as exc:
            cause = exc.errors()[0]["msg"]
            return CommandFailure(
                3,
                "FIXTURE_MALFORMED",
                f"synthetic step rejected before publication: {cause}",
            )
        raise RuntimeError("malformed fixture case was unexpectedly accepted")
    if scenario == "budget":
        return CommandFailure(
            4,
            "FIXTURE_BUDGET",
            "simulated budget stop at $0.00 spent; the fixture path made no provider call",
        )
    if scenario == "missing-input":
        return CommandFailure(
            2,
            "FIXTURE_INPUT",
            "fixture review requires --run-dir outside the repository root and dataset/",
        )
    if scenario == "interrupt":
        raise KeyboardInterrupt
    return None


def run_fixture_review(run_dir: Path, root: Path, scenario: str = "success") -> FixtureReview:
    if scenario not in SCENARIOS:
        raise CommandFailure(
            2,
            "FIXTURE_INPUT",
            "scenario must be one of: " + ", ".join(SCENARIOS),
        )
    destination = prepare_run_dir(run_dir, root)
    failure = _scenario_failure(scenario)
    if failure is not None:
        raise failure
    cases = synthetic_cases()
    csv_text = render_csv(cases)
    report_text = render_report(cases, destination)
    publish(destination, csv_text, report_text, fail_before_replace=scenario == "partial")
    lines = [
        "FIXTURE REVIEW",
        "Synthetic cases only. No evaluation dataset was read and output.csv was not written.",
        "[1/4] Load 3 synthetic cases",
        "[2/4] Validate deletion contracts",
        "[3/4] Publish isolated artifacts",
        "[4/4] Summarize finished verdicts",
        "COMPLETE        fixture_complete         2 verification steps",
        "INCOMPLETE      fixture_incomplete       finished verdict, 6 steps",
        "NOT_APPLICABLE  fixture_not_applicable   finished verdict, 0 steps",
        "INCOMPLETE is a completed review verdict. It is different from a failed command.",
        f"Report: {destination / 'fixture_review.md'}",
        f"CSV: {destination / 'fixture_cases.csv'}",
    ]
    return FixtureReview(lines=tuple(lines), run_dir=destination)
