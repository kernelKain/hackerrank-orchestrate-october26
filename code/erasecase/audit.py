"""Cutoff-safe intent, policy treatment, and contradiction checks.

Activity rows remain claims. A resource enters the plan only from participant
evidence linked by a supported identifier, or by a trace that identifies exactly
one subject. The planner, not a model, chooses operations and order.
"""

from __future__ import annotations

import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

from .evidence import extract_catalog
from .identity import build_identity_index
from .ingest import DatasetBundle, load_dataset

from .contracts import (
    CaseAssessment,
    DeletionRequest,
    DeletionRule,
    DeletionStatus,
    IdentifierFact,
    Observation,
    Operation,
    PolicyObligation,
)
from .evidence import EvidenceIndex, _strong_identifiers
from .identity import IdentityIndex
from .planner import Treatment, build_steps

IntentClassifier = Callable[[str], bool]

_DELETION = re.compile(
    r"("
    r"\b(delet\w*|eras\w*|remov\w*|forgotten|forget my)\b|"
    r"\bprofile is gone\b|\bcannot identify me\b|"
    r"\b(close|closed|closing)\b.{0,40}\b(account|profile|compte|cuenta|konto)\b|"
    r"\b(eliminar|eliminación|supprimer|suppression|löschen|apagar|excluir|usuń|verwijder|"
    r"cancellare|radera|slet|sil)\b|"
    r"削除|删除|消去"
    r")",
    re.IGNORECASE,
)
_REFUSAL = re.compile(
    r"("
    r"\b(do not|don't|dont|never)\b.{0,24}\b(delete|erase|remove|close)\b|"
    r"\b(keep|retain|conserve|conserver|mantener)\b.{0,32}\b(my |the )?(account|compte|cuenta)\b|"
    r"no eliminar|ne pas supprimer|nicht löschen"
    r")",
    re.IGNORECASE,
)
_ACCESS_ONLY = re.compile(
    r"("
    r"\b(export|access|correct|rectify|portability|unsubscribe)\b|"
    r"\bopt out\b|\bcopy of my data\b|\bdownload my data\b"
    r")",
    re.IGNORECASE,
)
_DELETED_ACCOUNT_REFERENCE = re.compile(
    r"deleted[- ]account|tombstone|internal (deleted|reference)|compte supprimé",
    re.IGNORECASE,
)

_ABSENT = {"not_found", "absent", "gone", "404", "410", "missing"}
_LOOKUP_KEYS = {
    "lookup_key",
    "query",
    "correlation_key",
    "subject_key",
    "match_key",
    "matched_value",
    "subject_selector",
}
_STORED_PII = {
    "email",
    "phone",
    "name",
    "full_name",
    "email_hash",
    "requester_email",
    "requester_name",
    "requester_phone",
    "display_name",
    "owner_email",
    "owner_phone",
    "customer_email",
    "page_email",
    "matched_value",
}
_ATTRIBUTION = {"user_id", "customer_reference", "subject_reference", "page_user_id"}
_KNOWN_SYSTEMS = {
    "account_service",
    "search_service",
    "support_platform",
    "analytics_platform",
    "security_service",
    "integration_service",
    "backup_service",
    "export_service",
    "identity_service",
    "legal_service",
}
_RESOURCE_ID = re.compile(
    r"^(?:account|search|support|analytics|backup|export|cache|data_flow|tombstone|email_delivery|audit_record)_[0-9]+$"
)
_FLOW_RULE = DeletionRule(
    rule_id="control_flow",
    data_category="DATA_FLOW",
    condition="An active process can copy or recreate the subject's data",
    required_action="DISABLE",
)

_PREFIX_CATEGORY = (
    ("tombstone_", "ACCOUNT_TOMBSTONE"),
    ("data_flow_", "DATA_FLOW"),
    ("audit_record_", "SECURITY_AUDIT_LOG"),
    ("account_", "USER_PROFILE"),
    ("search_", "SEARCH_INDEX_ENTRY"),
    ("analytics_", "ANALYTICS_PROFILE"),
    ("backup_", "BACKUP_ARCHIVE"),
    ("export_", "USER_EXPORT"),
    ("cache_", "CACHE_ENTRY"),
    ("email_delivery_", "EMAIL_DELIVERY_LOG"),
    ("support_", "SUPPORT_MESSAGE"),
)


class UnresolvedIntent(RuntimeError):
    """The request text does not authorize a deletion decision without review."""


@dataclass(frozen=True)
class AssessmentResult:
    case: CaseAssessment
    obligations: tuple[PolicyObligation, ...]
    contradictions: tuple[str, ...]


def deletion_authorized(text: str, classifier: IntentClassifier | None = None) -> bool:
    """Return whether the text authorizes deletion. Ambiguous text needs a classifier."""

    normalized = unicodedata.normalize("NFKC", text).casefold()
    deletion = _DELETION.search(normalized) is not None
    tombstone_reference = _DELETED_ACCOUNT_REFERENCE.search(normalized) is not None
    if _REFUSAL.search(normalized) and not tombstone_reference:
        return False
    if deletion:
        return True
    if _ACCESS_ONLY.search(normalized):
        return False
    if classifier is not None:
        return bool(classifier(text))
    raise UnresolvedIntent("request text does not determine deletion authorization")


def _blank(value: Any) -> bool:
    if value is None or isinstance(value, (dict, list)):
        return True
    return str(value).strip().casefold() in {"", "none", "null", "n/a", "nil"}


def _flag(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if _blank(value):
        return None
    token = str(value).strip().casefold()
    if token in {"true", "1", "yes", "active", "enabled"}:
        return True
    if token in {"false", "0", "no", "disabled", "blocked"}:
        return False
    return None


def _walk(value: Any, key: str = "") -> list[tuple[str, Any]]:
    found: list[tuple[str, Any]] = []
    if isinstance(value, dict):
        for child_key, child in value.items():
            found.extend(_walk(child, str(child_key)))
    elif isinstance(value, list):
        for child in value:
            found.extend(_walk(child, key))
    else:
        found.append((key, value))
    return found


def _tokens(observation: Observation) -> set[str]:
    tokens = {observation.state.casefold()}
    for key in ("result", "account_status", "status", "status_code", "http_status"):
        value = observation.facts.get(key)
        if not _blank(value):
            tokens.add(str(value).strip().casefold())
    return tokens


def _absent(observation: Observation) -> bool:
    return bool(_tokens(observation) & _ABSENT)


def _stored_pii(observation: Observation) -> bool:
    for key, value in _walk(observation.facts):
        if (
            key == "matched_value"
            and str(observation.facts.get("detector", "")).casefold() == "direct_identifier"
            and not _blank(value)
        ):
            return True
        if key in _LOOKUP_KEYS or _blank(value):
            continue
        if key in _STORED_PII or key.endswith(("_email", "_phone", "_name")):
            return True
    return False


def _attributable(observation: Observation) -> bool:
    if _stored_pii(observation):
        return True
    for key, value in _walk(observation.facts):
        if key in _ATTRIBUTION and not _blank(value):
            return True
    return False


def _text_blob(observations: tuple[Observation, ...]) -> str:
    parts: list[str] = []
    for observation in observations:
        for key, value in _walk(observation.facts):
            if isinstance(value, str):
                parts.append(value)
    return "\n".join(parts).casefold()


def _category(resource_id: str, observations: tuple[Observation, ...]) -> str:
    types = set()
    for observation in observations:
        record_type = observation.facts.get("record_type")
        if isinstance(record_type, str) and record_type.strip():
            types.add(record_type.strip().upper())
    if "ACCOUNT_TOMBSTONE" in types or resource_id.startswith("tombstone_"):
        return "ACCOUNT_TOMBSTONE"
    events = " ".join(str(item.facts.get("event", "")) for item in observations).casefold()
    if "contact_lookup" in events:
        return "SECONDARY_IDENTIFIER"
    for name in (
        "SUPPORT_ATTACHMENT",
        "SUPPORT_MESSAGE",
        "USER_PROFILE",
        "SEARCH_INDEX_ENTRY",
        "ANALYTICS_PROFILE",
        "PRODUCT_TELEMETRY",
        "DATA_FLOW",
        "BACKUP_ARCHIVE",
        "USER_EXPORT",
        "CACHE_ENTRY",
        "EMAIL_DELIVERY_LOG",
        "SECURITY_AUDIT_LOG",
        "LEGAL_HOLD_RECORD",
        "SECONDARY_IDENTIFIER",
        "MARKETING_PROFILE",
    ):
        if name in types:
            return name
    blob = _text_blob(observations)
    locations = " ".join(item.source_location for item in observations).casefold()
    events = " ".join(
        str(item.facts.get("event", "")) for item in observations
    ).casefold()
    has_message = any(
        isinstance(item.facts.get(key), str) and item.facts.get(key)
        for item in observations
        for key in ("message_excerpt", "message_text")
    )
    if resource_id.startswith("support_") and not has_message and (
        "attachment" in blob
        or "attachment" in locations
        or "uploader" in blob
        or "contact_query" in events
        or any(str(item.facts.get("marker_found", "")).casefold() == "false" for item in observations)
    ):
        return "SUPPORT_ATTACHMENT"
    for prefix, category in _PREFIX_CATEGORY:
        if resource_id.startswith(prefix):
            return category
    return "USER_PROFILE"


def _moment(observation: Observation) -> datetime:
    return observation.event_at or observation.captured_at


def _governing(observations: tuple[Observation, ...]) -> tuple[Observation, ...]:
    latest = max(_moment(item) for item in observations)
    return tuple(item for item in observations if _moment(item) == latest)


def _explicit_presence(observation: Observation) -> bool:
    if _explicit_absence(observation):
        return False
    tokens = _tokens(observation)
    if tokens & {"found", "200", "identifiable", "hit"}:
        return True
    if _stored_pii(observation):
        return True
    rows = observation.facts.get("rows")
    if isinstance(rows, int) and rows > 0 or (isinstance(rows, str) and rows.isdigit() and int(rows) > 0):
        return True
    marker = observation.facts.get("marker_found")
    return isinstance(marker, str) and marker.casefold() == "false"


def _explicit_absence(observation: Observation) -> bool:
    if _tokens(observation) & _ABSENT:
        return True
    rows = observation.facts.get("rows")
    return rows in {0, "0"}


def _evidence_id(observations: tuple[Observation, ...]) -> str:
    chosen = max(observations, key=lambda item: (item.captured_at, item.evidence_id))
    return chosen.evidence_id


def _posture(category: str, observations: tuple[Observation, ...]) -> str:
    action_tokens = set().union(*(_tokens(item) for item in observations))
    if category == "DATA_FLOW":
        flags = [_flag(item.facts.get("enabled")) for item in observations]
        if any(flag is True for flag in flags) or "active" in action_tokens:
            if any(flag is False for flag in flags) and not any(flag is True for flag in flags):
                return "FLOW_DISABLED"
            return "FLOW_ACTIVE"
        return "FLOW_DISABLED"
    if category == "BACKUP_ARCHIVE":
        blocked = []
        for item in observations:
            restore = _flag(item.facts.get("restore_allowed"))
            deletion_block = _flag(item.facts.get("deletion_block"))
            eligible = _flag(item.facts.get("eligible"))
            if restore is False or deletion_block is True or eligible is False:
                blocked.append(True)
            elif restore is True or deletion_block is False or eligible is True:
                blocked.append(False)
        if any(flag is False for flag in blocked) or (not blocked and "active" in action_tokens):
            return "RESTORE_OPEN"
        return "RESTORE_BLOCKED"
    if category in {
        "USER_PROFILE",
        "SECONDARY_IDENTIFIER",
        "SEARCH_INDEX_ENTRY",
        "CACHE_ENTRY",
        "USER_EXPORT",
        "MARKETING_PROFILE",
        "SUPPORT_ATTACHMENT",
    }:
        present = any(_explicit_presence(item) for item in observations)
        absent = any(_explicit_absence(item) for item in observations)
        if absent and not present:
            return "ABSENT"
        if not present:
            return "UNKNOWN"
        return "REMAINING"
    exposed = any(_stored_pii(item) for item in observations) or "identifiable" in action_tokens
    if category in {"ANALYTICS_PROFILE", "PRODUCT_TELEMETRY"}:
        if exposed or any(_attributable(item) for item in observations):
            return "EXPOSED"
        return "ANONYMIZED"
    if category in {"SUPPORT_MESSAGE", "EMAIL_DELIVERY_LOG", "ACCOUNT_TOMBSTONE"}:
        if exposed:
            return "EXPOSED"
        return "REDACTED"
    if category in {"SECURITY_AUDIT_LOG", "LEGAL_HOLD_RECORD"}:
        return "RETAINED"
    if category == "SUPPORT_ATTACHMENT":
        return "REMAINING"
    return "REMAINING"


def _treatment(category: str, posture: str) -> tuple[Operation | None, Operation | None, Operation]:
    """Map a category and observed posture to finding, remediation, and verification."""

    if category == "DATA_FLOW":
        if posture == "FLOW_ACTIVE":
            return (
                Operation.REPORT_ACTIVE_DATA_FLOW,
                Operation.DISABLE_DATA_FLOW,
                Operation.VERIFY_DATA_FLOW_DISABLED,
            )
        return None, None, Operation.VERIFY_DATA_FLOW_DISABLED
    if category == "BACKUP_ARCHIVE":
        if posture == "RESTORE_OPEN":
            return (
                Operation.REPORT_RESTORE_RISK,
                Operation.BLOCK_RESTORE,
                Operation.VERIFY_RESTORE_BLOCKED,
            )
        return None, None, Operation.VERIFY_RESTORE_BLOCKED
    if category in {"SECURITY_AUDIT_LOG", "LEGAL_HOLD_RECORD"}:
        return None, None, Operation.VERIFY_RECORD_PRESENT
    if category in {"ANALYTICS_PROFILE", "PRODUCT_TELEMETRY"}:
        if posture == "EXPOSED":
            return (
                Operation.REPORT_EXPOSED_PII,
                Operation.ANONYMIZE_RECORD,
                Operation.VERIFY_RECORD_ANONYMIZED,
            )
        return None, None, Operation.VERIFY_RECORD_ANONYMIZED
    if category in {"SUPPORT_MESSAGE", "EMAIL_DELIVERY_LOG", "ACCOUNT_TOMBSTONE"}:
        if posture == "EXPOSED":
            return (
                Operation.REPORT_EXPOSED_PII,
                Operation.REDACT_RECORD,
                Operation.VERIFY_RECORD_REDACTED,
            )
        return None, None, Operation.VERIFY_RECORD_REDACTED
    if posture == "ABSENT":
        return None, None, Operation.VERIFY_RECORD_ABSENT
    return (
        Operation.REPORT_REMAINING_RECORD,
        Operation.DELETE_RECORD,
        Operation.VERIFY_RECORD_ABSENT,
    )


def _trace_id(observation: Observation) -> str:
    for key in ("trace_id", "trace"):
        value = observation.facts.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def open_auditor(
    dataset_root: Path, *, classifier: IntentClassifier | None = None
) -> tuple[Auditor, DatasetBundle]:
    """Load participant data once and return an auditor that does not read labels."""

    bundle = load_dataset(dataset_root)
    identity = build_identity_index(bundle.identities, bundle.identity_events)
    catalog = extract_catalog(bundle.evidence_files, dataset_root, activities=bundle.activities)
    auditor = Auditor(
        identity,
        EvidenceIndex(catalog),
        bundle.rules,
        classifier=classifier,
    )
    return auditor, bundle


class Auditor:
    """Assess one request from an already built identity index and evidence index."""

    def __init__(
        self,
        identity: IdentityIndex,
        evidence: EvidenceIndex,
        rules: tuple[DeletionRule, ...],
        *,
        classifier: IntentClassifier | None = None,
    ) -> None:
        self.identity = identity
        self.evidence = evidence
        self.rules = rules
        self.classifier = classifier
        self._rules_by_category = {rule.data_category: rule for rule in rules}
        self._rules_by_category.setdefault("DATA_FLOW", _FLOW_RULE)
        self._origin_by_evidence = {
            item.evidence_id: item.origin for item in evidence.catalog.extractions
        }

    def assess(self, request: DeletionRequest) -> AssessmentResult:
        if not deletion_authorized(request.request_text, self.classifier):
            return AssessmentResult(
                case=CaseAssessment(
                    case_id=request.case_id,
                    deletion_status=DeletionStatus.NOT_APPLICABLE,
                    steps=(),
                ),
                obligations=(),
                contradictions=(),
            )
        subjects = self.identity.resolve_email(request.email, known_at=request.audit_at)
        if len(subjects) != 1:
            raise UnresolvedIntent(
                f"{request.case_id} resolves to {len(subjects)} supported subjects"
            )
        subject_id = next(iter(subjects))
        facts = self.identity.for_subject(subject_id, known_at=request.audit_at)
        linked = self._linked_observations(facts, request.audit_at)
        treatments, obligations = self._treat(linked)
        violations = tuple(item for item in treatments if not item.compliant)
        status = DeletionStatus.INCOMPLETE if violations else DeletionStatus.COMPLETE
        included = treatments if violations else tuple(item for item in treatments if item.compliant)
        steps = build_steps(included, complete=status is DeletionStatus.COMPLETE)
        contradictions: list[str] = []
        if request.reported_status == "COMPLETE" and violations:
            contradictions.append("workflow claimed COMPLETE while evidence shows a remaining obligation")
        if request.reported_status == "NOT_STARTED" and not violations and treatments:
            contradictions.append("workflow claimed NOT_STARTED while evidence shows the required state")
        return AssessmentResult(
            case=CaseAssessment(case_id=request.case_id, deletion_status=status, steps=steps),
            obligations=tuple(obligations),
            contradictions=tuple(contradictions),
        )

    def _linked_observations(
        self, facts: tuple[IdentifierFact, ...], audit_at: datetime
    ) -> tuple[Observation, ...]:
        subject_keys = {(fact.kind, fact.normalized_value) for fact in facts}
        available = tuple(
            observation
            for observation in self.evidence.catalog.observations
            if observation.facts.get("_source_type") != "activity_claim"
            and self.evidence._available(observation, audit_at)
        )
        direct_ids = {
            observation.observation_id
            for observation in available
            if _strong_identifiers(observation.facts) & subject_keys
        }
        traces: dict[str, set[str]] = defaultdict(set)
        for observation in available:
            trace = _trace_id(observation)
            if not trace or observation.observation_id not in direct_ids:
                continue
            traces[trace].add("subject")
        # A trace is usable only when every directly identified observation on it
        # belongs to this subject. Foreign identifiers make the trace ambiguous.
        ambiguous: set[str] = set()
        for observation in available:
            trace = _trace_id(observation)
            if not trace:
                continue
            keys = _strong_identifiers(observation.facts)
            if keys and not keys <= subject_keys and trace in traces:
                ambiguous.add(trace)
        inherited = {
            observation.observation_id
            for observation in available
            if (trace := _trace_id(observation))
            and trace in traces
            and trace not in ambiguous
        }
        chosen = direct_ids | inherited
        return tuple(
            observation for observation in available if observation.observation_id in chosen
        )

    def _treat(
        self, observations: tuple[Observation, ...]
    ) -> tuple[tuple[Treatment, ...], list[PolicyObligation]]:
        grouped: dict[tuple[str, str], list[Observation]] = defaultdict(list)
        for observation in observations:
            grouped[(observation.system_id, observation.resource_id)].append(observation)
        treatments: list[Treatment] = []
        obligations: list[PolicyObligation] = []
        moments: dict[tuple[str, str], datetime] = {}
        for (system_id, resource_id), items in grouped.items():
            if not _RESOURCE_ID.fullmatch(resource_id):
                continue
            bundle = tuple(items)
            origin = self._origin_by_evidence.get(bundle[0].evidence_id, "")
            if system_id not in _KNOWN_SYSTEMS and origin in _KNOWN_SYSTEMS:
                system_id = origin
            category = _category(resource_id, bundle)
            rule = self._rules_by_category.get(category)
            if rule is None:
                continue
            governing = _governing(bundle)
            posture = _posture(category, governing)
            if posture == "UNKNOWN":
                continue
            if posture == "ABSENT" and category in {
                "ANALYTICS_PROFILE",
                "PRODUCT_TELEMETRY",
                "SUPPORT_MESSAGE",
                "EMAIL_DELIVERY_LOG",
                "ACCOUNT_TOMBSTONE",
                "SECURITY_AUDIT_LOG",
                "LEGAL_HOLD_RECORD",
                "BACKUP_ARCHIVE",
            }:
                continue
            finding, remediation, verification = _treatment(category, posture)
            obligations.append(
                PolicyObligation(
                    rule_id=rule.rule_id,
                    data_category=rule.data_category,
                    condition=rule.condition,
                    required_action=rule.required_action,
                )
            )
            treatments.append(
                Treatment(
                    system_id=system_id,
                    resource_id=resource_id,
                    evidence_id=_evidence_id(governing),
                    verification=verification,
                    finding=finding,
                    remediation=remediation,
                )
            )
            moments[(system_id, resource_id)] = max(_moment(item) for item in governing)
        return _collapse_absent_profiles(treatments, obligations, moments)


def _collapse_absent_profiles(
    treatments: list[Treatment],
    obligations: list[PolicyObligation],
    moments: dict[tuple[str, str], datetime],
) -> tuple[tuple[Treatment, ...], list[PolicyObligation]]:
    """A later absent profile replaces an older absent lookup of the same subject."""

    absent = [
        item
        for item in treatments
        if item.resource_id.startswith("account_")
        and item.compliant
        and item.verification is Operation.VERIFY_RECORD_ABSENT
    ]
    if len(absent) <= 1:
        return tuple(treatments), obligations
    latest = max(
        absent,
        key=lambda item: (moments[(item.system_id, item.resource_id)], item.resource_id),
    )
    drop = {
        (item.system_id, item.resource_id)
        for item in absent
        if (item.system_id, item.resource_id) != (latest.system_id, latest.resource_id)
    }
    kept = [
        (treatment, obligation)
        for treatment, obligation in zip(treatments, obligations, strict=True)
        if (treatment.system_id, treatment.resource_id) not in drop
    ]
    return tuple(item[0] for item in kept), [item[1] for item in kept]
