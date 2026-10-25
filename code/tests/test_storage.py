from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from erasecase.contracts import (
    EvidenceExtraction,
    IdentifierFact,
    ModelCallRecord,
    Observation,
)
from erasecase.storage import RunStore


def test_run_store_records_one_model_call(tmp_path: Path) -> None:
    database = tmp_path / "run.sqlite3"
    record = ModelCallRecord(
        call_id="call-1",
        stage="probe",
        requested_model="example/model",
        attempts=1,
        latency_ms=15,
        outcome="ok",
    )
    with RunStore(database) as store:
        store.record_model_call(record)
    with RunStore(database) as store:
        count = store._connection.execute("SELECT COUNT(*) FROM model_calls").fetchone()[0]
    assert count == 1


def test_run_store_persists_extraction_and_identity_indexes(tmp_path: Path) -> None:
    captured_at = datetime(2026, 1, 1, tzinfo=timezone.utc)
    extraction = EvidenceExtraction(
        evidence_id="evidence_1",
        file_path="evidence/records/example.json",
        origin="records_service",
        captured_at=captured_at,
        media_type="application/json",
        sha256="a" * 64,
        byte_count=2,
        status="EXTRACTED",
        text="{}",
        observation_count=1,
    )
    observation = Observation(
        observation_id="observation_1",
        evidence_id="evidence_1",
        system_id="account_service",
        resource_id="account_1",
        captured_at=captured_at,
        state="PRESENT",
    )
    fact = IdentifierFact(
        subject_id="user_1",
        kind="email",
        normalized_value="person@example.com",
        original_value="person@example.com",
        available_at=captured_at,
        source_id="user_1",
    )
    database = tmp_path / "run.sqlite3"
    with RunStore(database) as store:
        store.record_evidence((extraction,), (observation,), ())
        store.record_identifier_facts((fact,))
    with RunStore(database) as store:
        assert store._connection.execute(
            "SELECT COUNT(*) FROM evidence_extractions"
        ).fetchone()[0] == 1
        assert store._connection.execute(
            "SELECT COUNT(*) FROM observations"
        ).fetchone()[0] == 1
        assert store._connection.execute(
            "SELECT COUNT(*) FROM identifier_facts"
        ).fetchone()[0] == 1
