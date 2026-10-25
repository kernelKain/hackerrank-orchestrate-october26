"""Safe, provenance-preserving extraction and cutoff-aware evidence indexing."""

from __future__ import annotations

import hashlib
import json
import re
import shlex
import sqlite3
import subprocess
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Iterator

from PIL import Image, UnidentifiedImageError

from .contracts import (
    EvidenceExtraction,
    EvidenceFile,
    ExtractionStatus,
    IdentifierFact,
    Observation,
    ResourceLink,
    SystemActivity,
)
from .identity import IdentityError, normalize_identifier

MAX_EVIDENCE_BYTES = 8 * 1024 * 1024
MAX_SQL_ROWS = 50_000
MAX_SQL_SECONDS = 3.0
RESOURCE_PATTERN = re.compile(r"\b(?:[A-Za-z][A-Za-z0-9]*[_-])+[0-9A-Za-z]+\b")
TIMESTAMP_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")
EMAIL_PATTERN = re.compile(r"(?<![\w.+-])[\w.!#$%&'*+/=?^`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![\w.-])")
USER_PATTERN = re.compile(r"\buser_[0-9]+\b", re.IGNORECASE)
HASH_PATTERN = re.compile(r"\b[0-9a-fA-F]{64}\b")


class EvidenceError(RuntimeError):
    """Evidence cannot be safely or completely extracted."""


@dataclass(frozen=True)
class EvidenceCatalog:
    extractions: tuple[EvidenceExtraction, ...]
    observations: tuple[Observation, ...]
    links: tuple[ResourceLink, ...]

    def require_complete(self, expected: Iterable[EvidenceFile]) -> None:
        expected_ids = {item.file_id for item in expected}
        actual_ids = {item.evidence_id for item in self.extractions}
        if expected_ids != actual_ids:
            missing = sorted(expected_ids - actual_ids)
            unexpected = sorted(actual_ids - expected_ids)
            raise EvidenceError(
                f"evidence extraction coverage mismatch missing={missing} unexpected={unexpected}"
            )


def _parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not TIMESTAMP_PATTERN.match(value):
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _observation_id(evidence_id: str, locator: str, resource_id: str) -> str:
    payload = f"{evidence_id}\0{locator}\0{resource_id}".encode()
    return "obs_" + hashlib.sha256(payload).hexdigest()[:24]


def _safe_path(dataset_root: Path, entry: EvidenceFile) -> Path:
    root = dataset_root.resolve()
    evidence_root = (root / "evidence").resolve()
    relative = Path(entry.file_path)
    if relative.is_absolute() or ".." in relative.parts:
        raise EvidenceError(f"{entry.file_id} path leaves dataset/evidence")
    unresolved = root / relative
    candidate = unresolved.resolve()
    if candidate == evidence_root or evidence_root not in candidate.parents:
        raise EvidenceError(f"{entry.file_id} path leaves dataset/evidence")
    if not candidate.is_file():
        raise EvidenceError(f"{entry.file_id} evidence file is missing")
    if unresolved.is_symlink() or any(
        parent.is_symlink()
        for parent in unresolved.parents
        if parent != root and root in parent.parents
    ):
        raise EvidenceError(f"{entry.file_id} evidence path must not be a symlink")
    return candidate


def _read_bytes(path: Path) -> bytes:
    size = path.stat().st_size
    if size > MAX_EVIDENCE_BYTES:
        raise EvidenceError(f"evidence file exceeds {MAX_EVIDENCE_BYTES} bytes: {path.name}")
    return path.read_bytes()


def _nearest_time(record: dict[str, Any], inherited: datetime | None) -> datetime | None:
    for key in (
        "observed_at",
        "captured_at",
        "recorded_at",
        "updated_at",
        "created_at",
        "exported_at",
        "event_time",
    ):
        parsed = _parse_datetime(record.get(key))
        if parsed is not None:
            return parsed
    return inherited


def _system_for(record: dict[str, Any], ancestry: tuple[str, ...], fallback: str) -> str:
    for key in ("system", "data_store", "origin_system", "service"):
        value = record.get(key)
        if isinstance(value, str) and value:
            return value
    for part in reversed(ancestry):
        if part.endswith(("_service", "_platform")):
            return part
    collection = next(
        (record.get(key) for key in ("collection", "collection_name") if record.get(key)),
        ancestry[-1] if ancestry else "",
    )
    prefixes = {
        "customer_profiles": "account_service",
        "customer_search": "search_service",
        "search_documents": "search_service",
        "customer_analytics": "analytics_platform",
        "support_": "support_platform",
        "customer_exports": "export_service",
        "connector_": "integration_service",
        "backup_": "backup_service",
        "security_": "security_service",
    }
    for prefix, system in prefixes.items():
        if isinstance(collection, str) and collection.startswith(prefix):
            return system
    return fallback


def _state_for(record: dict[str, Any]) -> str:
    for key in ("result", "state", "account_status", "status", "status_code"):
        value = record.get(key)
        if value is not None and str(value):
            return str(value)
    if "enabled" in record:
        return "ACTIVE" if bool(record["enabled"]) else "DISABLED"
    if "restore_allowed" in record:
        return "ACTIVE" if bool(record["restore_allowed"]) else "BLOCKED"
    return "PRESENT"


def _json_observations(
    payload: Any,
    entry: EvidenceFile,
    *,
    source_location: str,
) -> list[Observation]:
    observations: list[Observation] = []

    def walk(
        value: Any,
        ancestry: tuple[str, ...],
        inherited_time: datetime | None,
        inherited_system: str,
    ) -> None:
        if isinstance(value, dict):
            event_at = _nearest_time(value, inherited_time)
            system = _system_for(value, ancestry, inherited_system)
            resource = value.get("resource_id")
            if isinstance(resource, str) and resource:
                locator = "/".join(ancestry) or "$"
                observations.append(
                    Observation(
                        observation_id=_observation_id(entry.file_id, locator, resource),
                        evidence_id=entry.file_id,
                        system_id=system,
                        resource_id=resource,
                        captured_at=entry.captured_at,
                        event_at=event_at,
                        state=_state_for(value),
                        facts={**value, "_locator": locator, "_source_type": "evidence"},
                        source_location=source_location,
                    )
                )
            for key, child in value.items():
                walk(child, (*ancestry, str(key)), event_at, system)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, (*ancestry, str(index)), inherited_time, inherited_system)

    walk(payload, (), None, entry.origin)
    return observations


def _extract_json(
    data: bytes, entry: EvidenceFile, source_location: str
) -> tuple[str, list[Observation], tuple[str, ...]]:
    try:
        text = data.decode("utf-8")
        payload = json.loads(text)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceError(f"{entry.file_id} is not valid UTF-8 JSON") from exc
    return text, _json_observations(payload, entry, source_location=source_location), ()


def _parse_log_line(line: str) -> tuple[datetime | None, dict[str, Any]]:
    stripped = line.strip()
    if not stripped:
        return None, {}
    first, _, remainder = stripped.partition(" ")
    event_at = _parse_datetime(first)
    remainder = remainder.strip() if event_at else stripped
    if remainder.startswith("{"):
        try:
            payload = json.loads(remainder)
            return event_at, payload if isinstance(payload, dict) else {}
        except json.JSONDecodeError:
            return event_at, {}
    if " | " in remainder:
        parts = [part.strip(" -") for part in remainder.split("|")]
        if len(parts) >= 5:
            return event_at, {
                "system": parts[1],
                "resource_id": parts[2],
                "record_type": parts[3],
                "result": parts[4],
                "subject_reference": parts[5] if len(parts) > 5 else "",
            }
    payload: dict[str, Any] = {}
    try:
        tokens = shlex.split(remainder)
    except ValueError:
        tokens = remainder.split()
    for token in tokens:
        key, separator, value = token.partition("=")
        if separator and key:
            payload[key] = value
    return event_at, payload


def _extract_text(
    data: bytes, entry: EvidenceFile, source_location: str
) -> tuple[str, list[Observation], tuple[str, ...]]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise EvidenceError(f"{entry.file_id} is not valid UTF-8 text") from exc
    observations: list[Observation] = []
    pending_by_trace: dict[str, dict[str, Any]] = {}
    for line_number, line in enumerate(text.splitlines(), start=1):
        event_at, payload = _parse_log_line(line)
        resource = payload.get("resource_id")
        if not isinstance(resource, str) or not resource:
            resource = ""
        trace = payload.get("trace_id")
        if isinstance(trace, str) and trace and not resource:
            stored = pending_by_trace.setdefault(trace, {})
            for key, value in payload.items():
                stored.setdefault(key, value)
            continue
        if not resource:
            match = RESOURCE_PATTERN.search(line)
            resource = match.group(0) if match else ""
        if isinstance(trace, str) and trace in pending_by_trace:
            for key, value in pending_by_trace[trace].items():
                payload.setdefault(key, value)
        if not resource:
            continue
        payload.setdefault("raw_line", line)
        payload["_line"] = line_number
        locator = f"line:{line_number}"
        observations.append(
            Observation(
                observation_id=_observation_id(entry.file_id, locator, resource),
                evidence_id=entry.file_id,
                system_id=_system_for(payload, (), entry.origin),
                resource_id=resource,
                captured_at=entry.captured_at,
                event_at=event_at,
                state=_state_for(payload),
                facts={**payload, "_source_type": "evidence"},
                source_location=source_location,
            )
        )
    return text, observations, ()


def _sql_authorizer(action: int, arg1: str | None, arg2: str | None, *_: Any) -> int:
    allowed = {
        sqlite3.SQLITE_CREATE_INDEX,
        sqlite3.SQLITE_CREATE_TABLE,
        sqlite3.SQLITE_FUNCTION,
        sqlite3.SQLITE_INSERT,
        sqlite3.SQLITE_PRAGMA,
        sqlite3.SQLITE_READ,
        sqlite3.SQLITE_REINDEX,
        sqlite3.SQLITE_SELECT,
        sqlite3.SQLITE_TRANSACTION,
    }
    if action == sqlite3.SQLITE_PRAGMA and (arg1 or "").casefold() != "foreign_keys":
        return sqlite3.SQLITE_DENY
    if action == sqlite3.SQLITE_FUNCTION and (arg2 or "").casefold() not in {"json_valid"}:
        return sqlite3.SQLITE_DENY
    if action == sqlite3.SQLITE_UPDATE and arg1 == "sqlite_master":
        return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_OK if action in allowed else sqlite3.SQLITE_DENY


def _execute_sql_snapshot(text: str, entry: EvidenceFile) -> list[dict[str, Any]]:
    forbidden = re.compile(
        r"\b(?:ATTACH|DETACH|VACUUM|LOAD_EXTENSION|WRITABLE_SCHEMA|TEMP_STORE_DIRECTORY|READFILE|WRITEFILE|CREATE\s+(?:TRIGGER|VIEW|VIRTUAL))\b",
        re.IGNORECASE,
    )
    if forbidden.search(text):
        raise EvidenceError(f"{entry.file_id} contains a forbidden SQLite operation")
    connection = sqlite3.connect(":memory:")
    started = time.monotonic()
    steps = 0

    def progress() -> int:
        nonlocal steps
        steps += 1_000
        return int(steps > 2_000_000 or time.monotonic() - started > MAX_SQL_SECONDS)

    try:
        connection.enable_load_extension(False)
        connection.setlimit(sqlite3.SQLITE_LIMIT_ATTACHED, 0)
        connection.setlimit(sqlite3.SQLITE_LIMIT_SQL_LENGTH, MAX_EVIDENCE_BYTES)
        connection.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, MAX_EVIDENCE_BYTES)
        connection.set_progress_handler(progress, 1_000)
        connection.set_authorizer(_sql_authorizer)
        connection.executescript(text)
        connection.set_authorizer(None)
        tables = [
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            if isinstance(row[0], str) and not row[0].startswith("sqlite_")
        ]
        extracted: list[dict[str, Any]] = []
        for table in tables:
            quoted = '"' + table.replace('"', '""') + '"'
            cursor = connection.execute(f"SELECT * FROM {quoted} LIMIT ?", (MAX_SQL_ROWS + 1,))
            columns = [item[0] for item in cursor.description or ()]
            rows = cursor.fetchall()
            if len(rows) > MAX_SQL_ROWS:
                raise EvidenceError(f"{entry.file_id} exceeds the SQL row limit")
            for row_number, row in enumerate(rows, start=1):
                record = dict(zip(columns, row))
                record["_table"] = table
                record["_row"] = row_number
                encoded = record.get("record_json")
                if isinstance(encoded, str):
                    try:
                        nested = json.loads(encoded)
                    except json.JSONDecodeError as exc:
                        raise EvidenceError(
                            f"{entry.file_id} contains invalid record_json"
                        ) from exc
                    if isinstance(nested, dict):
                        record = {**record, **nested, "_record_json": nested}
                extracted.append(record)
        return extracted
    except sqlite3.Error as exc:
        raise EvidenceError(f"{entry.file_id} failed restricted SQLite import") from exc
    finally:
        connection.close()


def _extract_sql(
    data: bytes, entry: EvidenceFile, source_location: str
) -> tuple[str, list[Observation], tuple[str, ...]]:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise EvidenceError(f"{entry.file_id} is not valid UTF-8 SQL") from exc
    records = _execute_sql_snapshot(text, entry)
    observations: list[Observation] = []
    for record in records:
        resource = record.get("resource_id")
        if not isinstance(resource, str) or not resource:
            continue
        table = str(record["_table"])
        locator = f"table:{table}:row:{record['_row']}"
        observations.append(
            Observation(
                observation_id=_observation_id(entry.file_id, locator, resource),
                evidence_id=entry.file_id,
                system_id=_system_for(record, (table,), table),
                resource_id=resource,
                captured_at=entry.captured_at,
                event_at=_nearest_time(record, None),
                state=_state_for(record),
                facts={**record, "_source_type": "sql_snapshot"},
                source_location=source_location,
            )
        )
    return text, observations, (f"restricted SQLite rows={len(records)}",)


def _extract_pdf(
    path: Path, entry: EvidenceFile, source_location: str
) -> tuple[str, list[Observation], tuple[str, ...]]:
    try:
        completed = subprocess.run(
            ["pdftotext", "-layout", str(path), "-"],
            check=True,
            capture_output=True,
            timeout=15,
        )
        text = completed.stdout.decode("utf-8")
    except (OSError, subprocess.SubprocessError, UnicodeDecodeError) as exc:
        raise EvidenceError(f"{entry.file_id} PDF extraction failed") from exc
    if not text.strip():
        raise EvidenceError(f"{entry.file_id} PDF yielded no text")
    observations: list[Observation] = []
    for page_number, page in enumerate(text.split("\f"), start=1):
        page_emails = sorted({match.group(0) for match in EMAIL_PATTERN.finditer(page)})
        page_users = sorted({match.group(0) for match in USER_PATTERN.finditer(page)})
        for line_number, line in enumerate(page.splitlines(), start=1):
            resources = tuple(dict.fromkeys(match.group(0) for match in RESOURCE_PATTERN.finditer(line)))
            if not resources:
                continue
            locator = f"page:{page_number}:line:{line_number}"
            facts: dict[str, Any] = {
                "raw_line": line.strip(),
                "page": page_number,
                "line": line_number,
                "_source_type": "pdf_text",
            }
            if len(page_emails) == 1:
                facts["page_email"] = page_emails[0]
            if len(page_users) == 1:
                facts["page_user_id"] = page_users[0]
            for resource in resources:
                observations.append(
                    Observation(
                        observation_id=_observation_id(entry.file_id, locator, resource),
                        evidence_id=entry.file_id,
                        system_id=entry.origin,
                        resource_id=resource,
                        captured_at=entry.captured_at,
                        state="PRESENT",
                        facts=facts,
                        source_location=source_location,
                    )
                )
    return text, observations, (f"pdftotext pages={len(text.split(chr(12)))}",)


def _extract_image(
    path: Path, entry: EvidenceFile
) -> tuple[str, list[Observation], tuple[str, ...]]:
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            width, height = image.size
            mode = image.mode
            image_format = image.format
    except (OSError, UnidentifiedImageError) as exc:
        raise EvidenceError(f"{entry.file_id} is not a valid image") from exc
    if image_format != "PNG":
        raise EvidenceError(f"{entry.file_id} image is not PNG")
    return "", [], (f"validated PNG {width}x{height} mode={mode}; vision required",)


def extract_evidence(entry: EvidenceFile, dataset_root: Path) -> tuple[EvidenceExtraction, tuple[Observation, ...]]:
    path = _safe_path(dataset_root, entry)
    data = _read_bytes(path)
    source_location = str(Path(entry.file_path).as_posix())
    suffix = path.suffix.casefold()
    if suffix == ".json":
        media_type = "application/json"
        text, observations, diagnostics = _extract_json(data, entry, source_location)
        status = ExtractionStatus.EXTRACTED
    elif suffix in {".log", ".txt"}:
        media_type = "text/plain"
        text, observations, diagnostics = _extract_text(data, entry, source_location)
        status = ExtractionStatus.EXTRACTED
    elif suffix == ".sql":
        media_type = "application/sql"
        text, observations, diagnostics = _extract_sql(data, entry, source_location)
        status = ExtractionStatus.EXTRACTED
    elif suffix == ".pdf":
        media_type = "application/pdf"
        text, observations, diagnostics = _extract_pdf(path, entry, source_location)
        status = ExtractionStatus.EXTRACTED
    elif suffix == ".png":
        media_type = "image/png"
        text, observations, diagnostics = _extract_image(path, entry)
        status = ExtractionStatus.VISION_REQUIRED
    else:
        raise EvidenceError(f"{entry.file_id} has unsupported evidence type: {suffix}")
    extraction = EvidenceExtraction(
        evidence_id=entry.file_id,
        file_path=source_location,
        origin=entry.origin,
        captured_at=entry.captured_at,
        media_type=media_type,
        sha256=_digest(data),
        byte_count=len(data),
        status=status,
        text=text,
        observation_count=len(observations),
        diagnostics=diagnostics,
    )
    return extraction, tuple(observations)


def activity_observations(
    activities: Iterable[SystemActivity],
) -> tuple[tuple[Observation, ...], tuple[ResourceLink, ...]]:
    observations: list[Observation] = []
    links: list[ResourceLink] = []
    for activity in activities:
        observations.append(
            Observation(
                observation_id=f"activity-observation:{activity.activity_id}",
                evidence_id=activity.activity_id,
                system_id=activity.target_system,
                resource_id=activity.resource_id,
                captured_at=activity.event_time,
                event_at=activity.event_time,
                state=activity.reported_result,
                facts={
                    "event_type": activity.event_type,
                    "source_system": activity.source_system,
                    "target_system": activity.target_system,
                    "reported_result": activity.reported_result,
                    "details": activity.details,
                    "_source_type": "activity_claim",
                },
                source_location=f"system_activity.csv#{activity.activity_id}",
            )
        )
        if activity.source_system != activity.target_system:
            links.append(
                ResourceLink(
                    source_system_id=activity.source_system,
                    source_resource_id=activity.resource_id,
                    target_system_id=activity.target_system,
                    target_resource_id=activity.resource_id,
                    relationship=activity.event_type,
                    evidence_id=activity.activity_id,
                    event_at=activity.event_time,
                )
            )
    return tuple(observations), tuple(links)


def extract_catalog(
    entries: Iterable[EvidenceFile],
    dataset_root: Path,
    *,
    activities: Iterable[SystemActivity] = (),
) -> EvidenceCatalog:
    entry_tuple = tuple(entries)
    extractions: list[EvidenceExtraction] = []
    observations: list[Observation] = []
    for entry in entry_tuple:
        extraction, extracted_observations = extract_evidence(entry, dataset_root)
        extractions.append(extraction)
        observations.extend(extracted_observations)
    claimed_observations, links = activity_observations(activities)
    observations.extend(claimed_observations)
    catalog = EvidenceCatalog(tuple(extractions), tuple(observations), links)
    catalog.require_complete(entry_tuple)
    return catalog


def _walk_values(value: Any, parent_key: str = "") -> Iterator[tuple[str, str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield from _walk_values(child, str(key))
    elif isinstance(value, list):
        for child in value:
            yield from _walk_values(child, parent_key)
    elif isinstance(value, (str, int)):
        yield parent_key, str(value)


def _strong_identifiers(facts: dict[str, Any]) -> set[tuple[str, str]]:
    identifiers: set[tuple[str, str]] = set()
    for key, raw in _walk_values(facts):
        lowered = key.casefold()
        if lowered in {"raw_line", "details"} or lowered.startswith("_"):
            continue
        if raw.strip().casefold() in {"null", "none", "nil", "n/a", "undefined"}:
            continue
        candidates: list[tuple[str, str]] = []
        candidates.extend(("email", match.group(0)) for match in EMAIL_PATTERN.finditer(raw))
        candidates.extend(("user_id", match.group(0)) for match in USER_PATTERN.finditer(raw))
        if "email_hash" in lowered or (
            HASH_PATTERN.fullmatch(raw)
            and ("hash" in lowered or lowered in {"correlation_key", "subject_key", "lookup_key"})
        ):
            candidates.append(("email_hash", raw))
        elif "email" in lowered or lowered in {"lookup_key", "match_key", "matched_value", "subject_selector"}:
            candidates.extend(("email", match.group(0)) for match in EMAIL_PATTERN.finditer(raw))
        if lowered in {"user_id", "customer_reference", "subject_reference", "subject_ref", "correlation_key", "subject_key"}:
            candidates.extend(("user_id", match.group(0)) for match in USER_PATTERN.finditer(raw))
        if "phone" in lowered and len(re.sub(r"\D", "", raw)) >= 7:
            candidates.append(("phone", raw))
        for kind, candidate in candidates:
            try:
                identifiers.add((kind, normalize_identifier(kind, candidate)))
            except IdentityError:
                continue
    return identifiers


class EvidenceIndex:
    """Index only strong identifiers and enforce evidence availability at audit time."""

    def __init__(self, catalog: EvidenceCatalog) -> None:
        self.catalog = catalog
        by_identifier: dict[tuple[str, str], list[Observation]] = defaultdict(list)
        by_resource: dict[tuple[str, str], list[Observation]] = defaultdict(list)
        for observation in catalog.observations:
            by_resource[(observation.system_id, observation.resource_id)].append(observation)
            for identifier in _strong_identifiers(observation.facts):
                by_identifier[identifier].append(observation)
        self._by_identifier = {
            key: tuple(sorted(value, key=lambda item: (item.captured_at, item.observation_id)))
            for key, value in by_identifier.items()
        }
        self._by_resource = {
            key: tuple(sorted(value, key=lambda item: (item.captured_at, item.observation_id)))
            for key, value in by_resource.items()
        }

    @staticmethod
    def _available(observation: Observation, audit_at: datetime) -> bool:
        return observation.captured_at <= audit_at and (
            observation.event_at is None or observation.event_at <= audit_at
        )

    def for_identifiers(
        self,
        identifiers: Iterable[IdentifierFact],
        *,
        audit_at: datetime,
    ) -> tuple[Observation, ...]:
        matched: dict[str, Observation] = {}
        for fact in identifiers:
            for observation in self._by_identifier.get(
                (fact.kind, fact.normalized_value), ()
            ):
                if self._available(observation, audit_at):
                    matched[observation.observation_id] = observation
        return tuple(
            sorted(
                matched.values(),
                key=lambda item: (
                    item.event_at or item.captured_at,
                    item.system_id,
                    item.resource_id,
                    item.observation_id,
                ),
            )
        )

    def for_resource(
        self, system_id: str, resource_id: str, *, audit_at: datetime
    ) -> tuple[Observation, ...]:
        return tuple(
            item
            for item in self._by_resource.get((system_id, resource_id), ())
            if self._available(item, audit_at)
        )
