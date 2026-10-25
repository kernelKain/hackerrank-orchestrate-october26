from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from erasecase.contracts import IdentityAuditEvent, IdentitySnapshot
from erasecase.identity import IdentityError, build_identity_index, normalize_identifier
from erasecase.ingest import DatasetError, load_dataset
from erasecase.models import ROOT

UTC = timezone.utc


def test_participant_dataset_loads_with_strict_counts() -> None:
    bundle = load_dataset(ROOT / "dataset")
    assert len(bundle.requests) == 518
    assert len(bundle.evidence_files) == 94
    assert len(bundle.identities) > 500
    assert all(item.file_path.startswith("evidence/") for item in bundle.evidence_files)
    index = build_identity_index(bundle.identities, bundle.identity_events)
    assert all(
        len(index.resolve_email(request.email, known_at=request.audit_at)) == 1
        for request in bundle.requests
    )


def test_header_mismatch_fails_closed(tmp_path: Path) -> None:
    for name in (
        "deletion_requests.csv",
        "user_identities.csv",
        "user_audit_log.csv",
        "system_activity.csv",
        "deletion_rules.csv",
        "evidence_files.csv",
    ):
        (tmp_path / name).write_text("wrong\n", encoding="utf-8")
    with pytest.raises(DatasetError, match="header mismatch"):
        load_dataset(tmp_path)


def test_identity_history_resolves_current_and_historical_email() -> None:
    changed_at = datetime(2026, 2, 1, tzinfo=UTC)
    snapshot = IdentitySnapshot(
        user_id="user_1",
        name="Renée Example",
        email="new@example.com",
        phone="+1 (202) 555-0100",
        email_hash="b" * 64,
        updated_at=datetime(2026, 2, 2, tzinfo=UTC),
    )
    event = IdentityAuditEvent(
        audit_id="audit_1",
        user_id="user_1",
        event_time=changed_at,
        field_name="email",
        old_value="OLD@EXAMPLE.COM",
        new_value="new@example.com",
    )
    index = build_identity_index((snapshot,), (event,))
    known_at = datetime(2026, 2, 3, tzinfo=UTC)
    assert index.resolve_email("old@example.com", known_at=known_at) == {"user_1"}
    assert index.resolve_email("NEW@example.com", known_at=known_at) == {"user_1"}
    current = index.for_subject(
        "user_1", known_at=known_at, include_historical=False
    )
    emails = {fact.normalized_value for fact in current if fact.kind == "email"}
    assert emails == {"new@example.com"}
    assert normalize_identifier("phone", snapshot.phone) == "+12025550100"


def test_identity_chain_rejects_unsupported_links() -> None:
    snapshot = IdentitySnapshot(
        user_id="user_1",
        name="Example",
        email="final@example.com",
        phone="+12025550100",
        email_hash="b" * 64,
        updated_at=datetime(2026, 2, 3, tzinfo=UTC),
    )
    events = (
        IdentityAuditEvent(
            audit_id="audit_1",
            user_id="user_1",
            event_time=datetime(2026, 2, 1, tzinfo=UTC),
            field_name="email",
            old_value="old@example.com",
            new_value="middle@example.com",
        ),
        IdentityAuditEvent(
            audit_id="audit_2",
            user_id="user_1",
            event_time=datetime(2026, 2, 2, tzinfo=UTC),
            field_name="email",
            old_value="different@example.com",
            new_value="final@example.com",
        ),
    )
    with pytest.raises(IdentityError, match="broken email audit chain"):
        build_identity_index((snapshot,), events)
