"""Readable text shared by the fixture review and later live runs."""

from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass

from erasecase.contracts import CaseAssessment, OutputStep

STEP_KEY_ORDER = (
    "step_no",
    "phase",
    "system_id",
    "resource_id",
    "operation",
    "state",
    "evidence_id",
)


@dataclass(frozen=True)
class CommandFailure(Exception):
    """A finished command outcome with a stable code and a specific cause."""

    exit_code: int
    code: str
    message: str

    def render(self) -> str:
        return f"{self.code}: {self.message}"


def serialize_steps(steps: tuple[OutputStep, ...]) -> str:
    rows = []
    for step in steps:
        payload = step.model_dump(mode="json")
        rows.append({key: payload[key] for key in STEP_KEY_ORDER})
    return json.dumps(rows, separators=(",", ":"), ensure_ascii=True)


def render_csv(cases: tuple[CaseAssessment, ...]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["case_id", "deletion_status", "steps_json"])
    for case in sorted(cases, key=lambda item: item.case_id):
        writer.writerow(
            [case.case_id, case.deletion_status.value, serialize_steps(case.steps)]
        )
    text = buffer.getvalue()
    if not text.endswith("\n"):
        text += "\n"
    return text


def format_check(label: str, ok: bool, detail: str) -> str:
    status = "PASS" if ok else "FAIL"
    suffix = "" if ok else f" — next: {next_action(label, detail)}"
    return f"[{status}] {label}: {detail}{suffix}"


def next_action(label: str, detail: str) -> str:
    if label in {"pdftotext", "pdftoppm"}:
        return "install poppler-utils and rerun preflight"
    if label == "Python >= 3.12":
        return "rerun with Python 3.12 or newer"
    if label == "root .env ignored":
        return "keep the root .gitignore exclusion before storing a key"
    if label == "evidence directory":
        return "restore dataset/evidence and rerun preflight"
    if label.endswith(".csv"):
        return "restore the supplied participant file and rerun preflight"
    if label == "OpenRouter key configured" or "not configured" in detail:
        return "set OPENROUTER_API_KEY in the ignored root .env"
    if label.startswith("model "):
        return "confirm this model ID is enabled for the configured key"
    if label in {"OpenRouter authentication", "OpenRouter online check"}:
        return "check key access and network, then rerun preflight --online"
    return "resolve this check before a paid run"


def render_case_lines(case: CaseAssessment, summary: str) -> list[str]:
    lines = [
        f"case_id: {case.case_id}",
        f"deletion_status: {case.deletion_status.value}",
        "run_result: finished verdict",
        summary,
        "steps:",
    ]
    if not case.steps:
        lines.append("  (none)")
        return lines
    for step in case.steps:
        evidence = step.evidence_id or "(none — future work)"
        lines.append(
            f"  {step.step_no}. {step.phase.value} {step.operation.value} "
            f"{step.state.value} {step.system_id}/{step.resource_id} evidence={evidence}"
        )
    return lines
