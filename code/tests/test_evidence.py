from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from erasecase.contracts import EvidenceFile, ExtractionStatus, IdentifierFact
from erasecase.evidence import EvidenceError, EvidenceIndex, extract_catalog, extract_evidence
from erasecase.ingest import load_dataset
from erasecase.models import ROOT

UTC = timezone.utc


def entry(path: str, *, file_id: str = "evidence_test") -> EvidenceFile:
    return EvidenceFile(
        file_id=file_id,
        file_path=path,
        origin="test_service",
        captured_at=datetime(2026, 1, 2, tzinfo=UTC),
    )


def test_restricted_sql_extracts_primary_and_replica_rows(tmp_path: Path) -> None:
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    sql = evidence / "snapshot.sql"
    sql.write_text(
        """
        BEGIN;
        CREATE TABLE primary_copy(resource_id TEXT, origin_system TEXT, email TEXT, updated_at TEXT);
        CREATE TABLE replica_copy(resource_id TEXT, origin_system TEXT, email TEXT, updated_at TEXT);
        INSERT INTO primary_copy VALUES('account_1','account_service','old@example.com','2026-01-01T00:00:00Z');
        INSERT INTO replica_copy VALUES('account_1','replica_service','old@example.com','2026-01-01T00:01:00Z');
        COMMIT;
        """,
        encoding="utf-8",
    )
    extraction, observations = extract_evidence(entry("evidence/snapshot.sql"), tmp_path)
    assert extraction.status is ExtractionStatus.EXTRACTED
    assert {item.system_id for item in observations} == {
        "account_service",
        "replica_service",
    }
    assert all(item.resource_id == "account_1" for item in observations)


def test_restricted_sql_rejects_filesystem_operations(tmp_path: Path) -> None:
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    (evidence / "unsafe.sql").write_text(
        "ATTACH DATABASE '/tmp/escape.sqlite3' AS escape;",
        encoding="utf-8",
    )
    with pytest.raises(EvidenceError, match="forbidden SQLite operation"):
        extract_evidence(entry("evidence/unsafe.sql"), tmp_path)


def test_manifest_path_cannot_leave_evidence_directory(tmp_path: Path) -> None:
    (tmp_path / "evidence").mkdir()
    (tmp_path / "outside.txt").write_text("account_1", encoding="utf-8")
    with pytest.raises(EvidenceError, match="leaves dataset/evidence"):
        extract_evidence(entry("outside.txt"), tmp_path)


def test_full_manifest_has_an_explicit_outcome_for_every_file() -> None:
    bundle = load_dataset(ROOT / "dataset")
    catalog = extract_catalog(
        bundle.evidence_files,
        bundle.root,
        activities=bundle.activities,
    )
    assert len(catalog.extractions) == 94
    assert len({item.evidence_id for item in catalog.extractions}) == 94
    assert {item.status for item in catalog.extractions} == {
        ExtractionStatus.EXTRACTED,
        ExtractionStatus.VISION_REQUIRED,
    }
    assert sum(item.status is ExtractionStatus.VISION_REQUIRED for item in catalog.extractions) == 11
    assert all(item.sha256 and item.byte_count > 0 for item in catalog.extractions)
    assert all(
        item.text
        for item in catalog.extractions
        if item.status is ExtractionStatus.EXTRACTED
    )
    assert any(item.facts.get("_source_type") == "sql_snapshot" for item in catalog.observations)
    assert any(item.facts.get("_source_type") == "pdf_text" for item in catalog.observations)
    assert any(item.facts.get("_source_type") == "activity_claim" for item in catalog.observations)
    delivery = [
        item
        for item in catalog.observations
        if item.evidence_id == "evidence_58" and item.resource_id == "support_001"
    ]
    assert delivery
    assert {item.facts.get("page_email") for item in delivery} == {
        "priya.raman@gmail.com"
    }


def test_identifier_lookup_respects_capture_and_event_cutoffs(tmp_path: Path) -> None:
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    (evidence / "records.json").write_text(
        """{"records":[
        {"resource_id":"account_1","system":"account_service","email":"person@example.com","observed_at":"2026-01-01T00:00:00Z"},
        {"resource_id":"account_2","system":"account_service","email":"person@example.com","observed_at":"2026-01-03T00:00:00Z"},
        {"resource_id":"account_3","system":"account_service","display_name":"Person Example","observed_at":"2026-01-01T00:00:00Z"}
        ]}""",
        encoding="utf-8",
    )
    manifest = (
        EvidenceFile(
            file_id="evidence_1",
            file_path="evidence/records.json",
            origin="records_service",
            captured_at=datetime(2026, 1, 2, tzinfo=UTC),
        ),
    )
    index = EvidenceIndex(extract_catalog(manifest, tmp_path))
    identifier = IdentifierFact(
        subject_id="user_1",
        kind="email",
        normalized_value="person@example.com",
        original_value="person@example.com",
        available_at=datetime(2026, 1, 1, tzinfo=UTC),
        source_id="user_1",
    )
    matched = index.for_identifiers(
        (identifier,), audit_at=datetime(2026, 1, 2, 12, tzinfo=UTC)
    )
    assert [item.resource_id for item in matched] == ["account_1"]
    assert "account_3" not in {item.resource_id for item in matched}


def test_trace_copies_one_identifier_onto_a_later_line(tmp_path: Path) -> None:
    evidence = tmp_path / "evidence" / "logs"
    evidence.mkdir(parents=True)
    (evidence / "trace.log").write_text(
        "\n".join(
            [
                "2026-01-02T00:00:00Z trace_id=tr-1 resource_id=account_1 lookup_key=ada@example.com event=profile_lookup_started",
                "2026-01-02T00:00:01Z trace_id=tr-1 resource_id=account_9 rows=0 http_status=404 event=profile_lookup_completed",
            ]
        ),
        encoding="utf-8",
    )
    _extraction, observations = extract_evidence(entry("evidence/logs/trace.log"), tmp_path)
    later = next(item for item in observations if item.resource_id == "account_9")
    assert later.facts["link_email"] == "ada@example.com"
    assert "email" not in later.facts


def test_trace_with_two_identifiers_is_not_propagated(tmp_path: Path) -> None:
    evidence = tmp_path / "evidence" / "logs"
    evidence.mkdir(parents=True)
    (evidence / "trace.log").write_text(
        "\n".join(
            [
                "2026-01-02T00:00:00Z trace_id=tr-2 resource_id=account_1 lookup_key=ada@example.com",
                "2026-01-02T00:00:01Z trace_id=tr-2 resource_id=account_2 lookup_key=other@example.com",
                "2026-01-02T00:00:02Z trace_id=tr-2 resource_id=account_3 rows=0",
            ]
        ),
        encoding="utf-8",
    )
    _extraction, observations = extract_evidence(entry("evidence/logs/trace.log"), tmp_path)
    blank = next(item for item in observations if item.resource_id == "account_3")
    assert "link_email" not in blank.facts

