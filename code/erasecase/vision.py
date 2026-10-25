"""Screenshot reading with abstention. The model does not choose audit steps."""

from __future__ import annotations

import base64
import json
import re
from pathlib import Path
from typing import Any

from erasecase.contracts import EvidenceFile, Observation
from erasecase.evidence import _observation_id
from erasecase.models import ROOT, VISION_CANDIDATE, OpenRouterClient, ProviderError, require_known_cost

RESOURCE_ID = re.compile(
    r"^(?:account|search|support|analytics|backup|export|cache|data_flow|tombstone|email_delivery|audit_record)_[0-9]+$"
)
EMAIL = re.compile(r"^[\w.!#$%&'*+/=?^`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
USER_ID = re.compile(r"^user_[0-9]+$", re.IGNORECASE)
EMAIL_HASH = re.compile(r"^[0-9a-fA-F]{64}$")
POSTURES = {"present", "absent", "redacted", "anonymized", "unknown"}
PREFIX_SYSTEM = {
    "account_": "account_service",
    "tombstone_": "account_service",
    "search_": "search_service",
    "support_": "support_platform",
    "analytics_": "analytics_platform",
    "backup_": "backup_service",
    "export_": "export_service",
    "cache_": "cache_service",
    "data_flow_": "integration_service",
    "email_delivery_": "account_service",
    "audit_record_": "security_service",
}
PREFIX_TYPE = {
    "account_": "USER_PROFILE",
    "tombstone_": "ACCOUNT_TOMBSTONE",
    "search_": "SEARCH_INDEX_ENTRY",
    "support_": "SUPPORT_MESSAGE",
    "analytics_": "ANALYTICS_PROFILE",
    "backup_": "BACKUP_ARCHIVE",
    "export_": "USER_EXPORT",
    "cache_": "CACHE_ENTRY",
    "data_flow_": "DATA_FLOW",
    "email_delivery_": "EMAIL_DELIVERY_LOG",
    "audit_record_": "SECURITY_AUDIT_LOG",
}
VISION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["nothing_identifiable", "records"],
    "properties": {
        "nothing_identifiable": {"type": "boolean"},
        "records": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["resource_id", "email", "phone", "user_id", "email_hash", "posture"],
                "properties": {
                    "resource_id": {"type": "string"},
                    "email": {"type": "string"},
                    "phone": {"type": "string"},
                    "user_id": {"type": "string"},
                    "email_hash": {"type": "string"},
                    "posture": {"type": "string"},
                },
            },
        },
    },
}


def vision_cache_dir() -> Path | None:
    path = ROOT / "runs" / "vision"
    if (path / "manifest.json").is_file():
        return path
    return None


def observations_from_screen(entry: EvidenceFile, payload: dict[str, Any]) -> tuple[Observation, ...]:
    """Accept a screen reading only when a resource id and a strong identifier are both present."""

    if payload.get("nothing_identifiable") is True:
        return ()
    records = payload.get("records")
    if not isinstance(records, list):
        return ()
    observations: list[Observation] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        built = _one_record(entry, record)
        if built is not None:
            observations.append(built)
    return tuple(observations)


def load_image_observations(
    cache_dir: Path,
    entries: tuple[EvidenceFile, ...],
    dataset_root: Path,
) -> dict[str, tuple[Observation, ...]]:
    """Load cached screen readings. Files absent from the cache stay unread."""

    loaded: dict[str, tuple[Observation, ...]] = {}
    known = {item.file_id: item for item in entries}
    manifest_path = cache_dir / "manifest.json"
    if not manifest_path.is_file():
        return loaded
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return loaded
    files = manifest.get("files") if isinstance(manifest, dict) else None
    if not isinstance(files, dict):
        return loaded
    for file_id, raw in files.items():
        entry = known.get(file_id)
        if entry is None or not isinstance(raw, dict):
            continue
        if raw.get("sha256") != _file_sha(dataset_root, entry):
            continue
        payload = raw.get("payload")
        if isinstance(payload, dict):
            loaded[file_id] = observations_from_screen(entry, payload)
    return loaded


def read_screenshots(
    entries: tuple[EvidenceFile, ...],
    dataset_root: Path,
    cache_dir: Path,
    *,
    budget_usd: float,
) -> dict[str, Any]:
    """Read PNG evidence within budget. A failed or empty screen is an abstention."""

    if budget_usd <= 0:
        raise ProviderError("vision budget must be greater than 0")
    images = [item for item in entries if item.file_path.lower().endswith(".png")]
    cache_dir.mkdir(parents=True, exist_ok=True)
    manifest = _read_manifest(cache_dir)
    files = manifest.setdefault("files", {})
    if not isinstance(files, dict):
        files = {}
        manifest["files"] = files
    pending = []
    for entry in images:
        cached = files.get(entry.file_id)
        digest = _file_sha(dataset_root, entry)
        if isinstance(cached, dict) and cached.get("sha256") == digest and isinstance(cached.get("payload"), dict):
            continue
        pending.append(entry)
    spent = float(manifest.get("cost_usd") or 0)
    calls = int(manifest.get("calls") or 0)
    if pending:
        client = OpenRouterClient(read_timeout=90)
        catalog = {item.get("id"): item for item in client.models()}
        model = catalog.get(VISION_CANDIDATE)
        if not isinstance(model, dict):
            raise ProviderError("vision model is unavailable")
        from erasecase.models import estimate_probe_cost

        reservation = estimate_probe_cost(model, input_tokens=2_000, output_tokens=2_000, images=1)
        for entry in pending:
            if spent + reservation > budget_usd:
                break
            try:
                payload, usage = client.read_screen(_data_url(_image_path(dataset_root, entry)))
            except ProviderError as exc:
                print(f"vision unresolved: {entry.file_id}: {exc}")
                continue
            cost = require_known_cost(usage.get("cost_usd"))
            spent += cost
            calls += 1
            digest = _file_sha(dataset_root, entry)
            accepted = observations_from_screen(entry, payload)
            stored = payload if accepted or payload.get("nothing_identifiable") is True else {
                "nothing_identifiable": True,
                "records": [],
            }
            files[entry.file_id] = {
                "sha256": digest,
                "payload": stored,
                "accepted_records": len(accepted),
                "model": usage.get("model"),
                "provider": usage.get("provider"),
                "input_tokens": usage.get("input_tokens"),
                "output_tokens": usage.get("output_tokens"),
                "cost_usd": cost,
            }
            manifest["calls"] = calls
            manifest["cost_usd"] = round(spent, 6)
            (cache_dir / "manifest.json").write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
    manifest["calls"] = calls
    manifest["cost_usd"] = round(spent, 6)
    manifest["input_tokens"] = sum(int(item.get("input_tokens") or 0) for item in files.values() if isinstance(item, dict))
    manifest["output_tokens"] = sum(int(item.get("output_tokens") or 0) for item in files.values() if isinstance(item, dict))
    manifest["model"] = VISION_CANDIDATE
    (cache_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def _one_record(entry: EvidenceFile, record: dict[str, Any]) -> Observation | None:
    resource_id = str(record.get("resource_id") or "").strip()
    posture = str(record.get("posture") or "").strip().casefold()
    if not RESOURCE_ID.fullmatch(resource_id) or posture not in POSTURES or posture == "unknown":
        return None
    email = _clean(record.get("email"), EMAIL)
    phone_digits = re.sub(r"\D", "", str(record.get("phone") or ""))
    phone = f"+{phone_digits}" if len(phone_digits) >= 7 else ""
    user_id = _clean(record.get("user_id"), USER_ID)
    email_hash = _clean(record.get("email_hash"), EMAIL_HASH)
    if not any((email, phone, user_id, email_hash)):
        return None
    if posture == "anonymized" and (email or phone or user_id):
        posture = "present"
    prefix = next(prefix for prefix in PREFIX_SYSTEM if resource_id.startswith(prefix))
    system_id = PREFIX_SYSTEM[prefix]
    record_type = PREFIX_TYPE[prefix]
    if posture == "present":
        facts = {"record_type": record_type, "_source_type": "vision", "posture": posture}
        if email:
            facts["email"] = email
        if phone:
            facts["phone"] = phone
        if user_id:
            facts["user_id"] = user_id.casefold()
        if email_hash:
            facts["email_hash"] = email_hash.casefold()
        state = "PRESENT"
    elif posture == "absent":
        facts = {
            "record_type": record_type,
            "_source_type": "vision",
            "posture": posture,
            "rows": 0,
            "http_status": "404",
        }
        _put_links(facts, email, phone, user_id, email_hash)
        state = "404"
    else:
        facts = {"record_type": record_type, "_source_type": "vision", "posture": posture}
        if posture == "redacted" and resource_id.startswith("tombstone_") and user_id:
            facts["user_id"] = user_id.casefold()
            email = phone = email_hash = ""
        _put_links(facts, email, phone, "" if posture == "redacted" else user_id, email_hash)
        state = "REDACTED" if posture == "redacted" else "ANONYMIZED"
    if resource_id.startswith("data_flow_"):
        facts["enabled"] = posture == "present"
    if resource_id.startswith("backup_"):
        facts["restore_allowed"] = posture == "present"
    return Observation(
        observation_id=_observation_id(entry.file_id, f"vision:{resource_id}", resource_id),
        evidence_id=entry.file_id,
        system_id=system_id,
        resource_id=resource_id,
        captured_at=entry.captured_at,
        state=state,
        facts=facts,
        source_location=entry.file_path,
    )


def _put_links(facts: dict[str, Any], email: str, phone: str, user_id: str, email_hash: str) -> None:
    if email:
        facts["link_email"] = email
    if phone:
        facts["link_phone"] = phone
    if user_id:
        facts["link_user_id"] = user_id.casefold()
    if email_hash:
        facts["link_email_hash"] = email_hash.casefold()


def _clean(value: Any, pattern: re.Pattern[str]) -> str:
    text = str(value or "").strip()
    return text if pattern.fullmatch(text) else ""


def _image_path(dataset_root: Path, entry: EvidenceFile) -> Path:
    from erasecase.evidence import _safe_path

    return _safe_path(dataset_root, entry)


def _data_url(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _file_sha(dataset_root: Path, entry: EvidenceFile) -> str:
    import hashlib

    return hashlib.sha256(_image_path(dataset_root, entry).read_bytes()).hexdigest()


def _read_manifest(cache_dir: Path) -> dict[str, Any]:
    path = cache_dir / "manifest.json"
    if not path.is_file():
        return {"files": {}, "calls": 0, "cost_usd": 0, "input_tokens": 0, "output_tokens": 0}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"files": {}, "calls": 0, "cost_usd": 0, "input_tokens": 0, "output_tokens": 0}
    return payload if isinstance(payload, dict) else {"files": {}, "calls": 0, "cost_usd": 0}
