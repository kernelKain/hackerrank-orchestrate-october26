"""Strict participant-dataset ingestion with explicit source boundaries."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, TypeVar

from pydantic import BaseModel, ValidationError

from .contracts import (
    DeletionRequest,
    DeletionRule,
    EvidenceFile,
    IdentityAuditEvent,
    IdentitySnapshot,
    SystemActivity,
)

T = TypeVar("T", bound=BaseModel)


class DatasetError(RuntimeError):
    """Participant input is missing, malformed, or outside the approved boundary."""


@dataclass(frozen=True)
class DatasetBundle:
    root: Path
    requests: tuple[DeletionRequest, ...]
    identities: tuple[IdentitySnapshot, ...]
    identity_events: tuple[IdentityAuditEvent, ...]
    activities: tuple[SystemActivity, ...]
    rules: tuple[DeletionRule, ...]
    evidence_files: tuple[EvidenceFile, ...]


HEADERS: dict[str, tuple[str, ...]] = {
    "deletion_requests.csv": (
        "case_id",
        "email",
        "requested_at",
        "reported_status",
        "reported_at",
        "audit_at",
        "request_text",
    ),
    "user_identities.csv": (
        "user_id",
        "name",
        "email",
        "phone",
        "email_hash",
        "updated_at",
    ),
    "user_audit_log.csv": (
        "audit_id",
        "user_id",
        "event_time",
        "field_name",
        "old_value",
        "new_value",
    ),
    "system_activity.csv": (
        "activity_id",
        "event_time",
        "event_type",
        "source_system",
        "target_system",
        "resource_id",
        "reported_result",
        "details",
    ),
    "deletion_rules.csv": (
        "rule_id",
        "data_category",
        "condition",
        "required_action",
    ),
    "evidence_files.csv": ("file_id", "file_path", "origin", "captured_at"),
}


def _read_models(path: Path, model: type[T]) -> tuple[T, ...]:
    expected = HEADERS[path.name]
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if tuple(reader.fieldnames or ()) != expected:
                raise DatasetError(
                    f"{path.name} header mismatch: expected {','.join(expected)}"
                )
            rows: list[T] = []
            for line_number, row in enumerate(reader, start=2):
                try:
                    rows.append(model.model_validate(row))
                except ValidationError as exc:
                    raise DatasetError(
                        f"{path.name}:{line_number} violates {model.__name__}"
                    ) from exc
    except OSError as exc:
        raise DatasetError(f"cannot read participant file {path.name}") from exc
    return tuple(rows)


def _unique(items: tuple[T, ...], key: Callable[[T], str], label: str) -> None:
    seen: set[str] = set()
    for item in items:
        value = key(item)
        if value in seen:
            raise DatasetError(f"duplicate {label}: {value}")
        seen.add(value)


def load_dataset(dataset_root: Path) -> DatasetBundle:
    """Load only the participant-facing files below ``dataset_root``."""

    root = dataset_root.resolve()
    if not root.is_dir():
        raise DatasetError(f"dataset root is not a directory: {root}")
    requests = _read_models(root / "deletion_requests.csv", DeletionRequest)
    identities = _read_models(root / "user_identities.csv", IdentitySnapshot)
    identity_events = _read_models(root / "user_audit_log.csv", IdentityAuditEvent)
    activities = _read_models(root / "system_activity.csv", SystemActivity)
    rules = _read_models(root / "deletion_rules.csv", DeletionRule)
    evidence_files = _read_models(root / "evidence_files.csv", EvidenceFile)

    _unique(requests, lambda item: item.case_id, "case_id")
    _unique(identities, lambda item: item.user_id, "user_id")
    _unique(identity_events, lambda item: item.audit_id, "audit_id")
    _unique(activities, lambda item: item.activity_id, "activity_id")
    _unique(rules, lambda item: item.rule_id, "rule_id")
    _unique(evidence_files, lambda item: item.file_id, "file_id")

    known_users = {item.user_id for item in identities}
    unknown_events = sorted(
        {item.user_id for item in identity_events if item.user_id not in known_users}
    )
    if unknown_events:
        raise DatasetError(
            "identity audit references unknown users: " + ", ".join(unknown_events[:5])
        )

    return DatasetBundle(
        root=root,
        requests=requests,
        identities=identities,
        identity_events=identity_events,
        activities=activities,
        rules=rules,
        evidence_files=evidence_files,
    )
