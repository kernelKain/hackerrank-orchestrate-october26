"""Transactional local run state and usage accounting."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from .contracts import (
    CONTRACT_VERSION,
    EvidenceExtraction,
    IdentifierFact,
    ModelCallRecord,
    Observation,
    ResourceLink,
)

SCHEMA_VERSION = 2


class RunStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(path)
        self._connection.execute("PRAGMA journal_mode=WAL")
        self._connection.execute("PRAGMA foreign_keys=ON")
        self._initialize()

    def _initialize(self) -> None:
        with self.transaction() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS model_calls (
                    call_id TEXT PRIMARY KEY,
                    payload_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS evidence_extractions (
                    evidence_id TEXT PRIMARY KEY,
                    payload_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS observations (
                    observation_id TEXT PRIMARY KEY,
                    payload_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS identifier_facts (
                    fact_id TEXT PRIMARY KEY,
                    payload_json TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS resource_links (
                    link_id TEXT PRIMARY KEY,
                    payload_json TEXT NOT NULL
                );
                """
            )
            expected = {
                "schema_version": str(SCHEMA_VERSION),
                "contract_version": CONTRACT_VERSION,
            }
            for key, value in expected.items():
                row = connection.execute(
                    "SELECT value FROM metadata WHERE key = ?", (key,)
                ).fetchone()
                if row is not None and row[0] != value:
                    raise RuntimeError(f"incompatible run store {key}: {row[0]}")
                connection.execute(
                    "INSERT OR IGNORE INTO metadata(key, value) VALUES (?, ?)",
                    (key, value),
                )

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        try:
            self._connection.execute("BEGIN IMMEDIATE")
            yield self._connection
        except Exception:
            self._connection.rollback()
            raise
        else:
            self._connection.commit()

    def record_model_call(self, record: ModelCallRecord) -> None:
        payload = json.dumps(record.model_dump(mode="json"), sort_keys=True)
        with self.transaction() as connection:
            connection.execute(
                "INSERT INTO model_calls(call_id, payload_json) VALUES (?, ?)",
                (record.call_id, payload),
            )

    @staticmethod
    def _payload(value: object) -> str:
        return json.dumps(value, sort_keys=True, separators=(",", ":"))

    @staticmethod
    def _content_id(prefix: str, payload: str) -> str:
        return f"{prefix}:" + hashlib.sha256(payload.encode()).hexdigest()

    def record_evidence(
        self,
        extractions: tuple[EvidenceExtraction, ...],
        observations: tuple[Observation, ...],
        links: tuple[ResourceLink, ...],
    ) -> None:
        with self.transaction() as connection:
            for extraction in extractions:
                payload = self._payload(extraction.model_dump(mode="json"))
                connection.execute(
                    "INSERT OR REPLACE INTO evidence_extractions(evidence_id, payload_json) VALUES (?, ?)",
                    (extraction.evidence_id, payload),
                )
            for observation in observations:
                payload = self._payload(observation.model_dump(mode="json"))
                connection.execute(
                    "INSERT OR REPLACE INTO observations(observation_id, payload_json) VALUES (?, ?)",
                    (observation.observation_id, payload),
                )
            for link in links:
                payload = self._payload(link.model_dump(mode="json"))
                link_id = self._content_id("link", payload)
                connection.execute(
                    "INSERT OR REPLACE INTO resource_links(link_id, payload_json) VALUES (?, ?)",
                    (link_id, payload),
                )

    def record_identifier_facts(self, facts: tuple[IdentifierFact, ...]) -> None:
        with self.transaction() as connection:
            for fact in facts:
                payload = self._payload(fact.model_dump(mode="json"))
                fact_id = self._content_id("identity", payload)
                connection.execute(
                    "INSERT OR REPLACE INTO identifier_facts(fact_id, payload_json) VALUES (?, ?)",
                    (fact_id, payload),
                )

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> RunStore:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
