"""Time-aware identity history reconstructed from snapshots and audit events."""

from __future__ import annotations

import re
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone

from .contracts import IdentifierFact, IdentityAuditEvent, IdentitySnapshot

SUPPORTED_FIELDS = ("name", "email", "phone", "email_hash")


class IdentityError(RuntimeError):
    """Identity history is internally inconsistent or unsupported."""


def normalize_identifier(kind: str, value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).strip()
    if kind == "email":
        local, separator, domain = normalized.partition("@")
        if not separator or not local or not domain:
            raise IdentityError("invalid email identifier")
        return f"{local.casefold()}@{domain.casefold()}"
    if kind == "phone":
        digits = re.sub(r"\D", "", normalized)
        if not digits:
            raise IdentityError("invalid phone identifier")
        return f"+{digits}"
    if kind in {"email_hash", "user_id"}:
        return normalized.casefold()
    if kind == "name":
        return " ".join(normalized.casefold().split())
    raise IdentityError(f"unsupported identifier kind: {kind}")


class IdentityIndex:
    """Preserve every supported identifier fact without merging on names alone."""

    def __init__(self, facts: tuple[IdentifierFact, ...]) -> None:
        self.facts = tuple(
            sorted(
                facts,
                key=lambda item: (
                    item.subject_id,
                    item.kind,
                    item.valid_from or datetime.min.replace(tzinfo=timezone.utc),
                    item.normalized_value,
                    item.source_id,
                ),
            )
        )
        by_value: dict[tuple[str, str], set[str]] = defaultdict(set)
        by_subject: dict[str, list[IdentifierFact]] = defaultdict(list)
        for fact in self.facts:
            by_value[(fact.kind, fact.normalized_value)].add(fact.subject_id)
            by_subject[fact.subject_id].append(fact)
        self._by_value = {key: frozenset(value) for key, value in by_value.items()}
        self._by_subject = {key: tuple(value) for key, value in by_subject.items()}

    def resolve(self, kind: str, value: str, *, known_at: datetime) -> frozenset[str]:
        normalized = normalize_identifier(kind, value)
        subjects = self._by_value.get((kind, normalized), frozenset())
        return frozenset(
            subject
            for subject in subjects
            if any(
                fact.kind == kind
                and fact.normalized_value == normalized
                and (fact.available_at is None or fact.available_at <= known_at)
                for fact in self._by_subject[subject]
            )
        )

    def resolve_email(self, email: str, *, known_at: datetime) -> frozenset[str]:
        return self.resolve("email", email, known_at=known_at)

    def for_subject(
        self,
        subject_id: str,
        *,
        known_at: datetime,
        include_historical: bool = True,
    ) -> tuple[IdentifierFact, ...]:
        facts = []
        for fact in self._by_subject.get(subject_id, ()):
            if fact.available_at is not None and fact.available_at > known_at:
                continue
            if not include_historical:
                if fact.valid_from is not None and fact.valid_from > known_at:
                    continue
                if fact.valid_to is not None and known_at >= fact.valid_to:
                    continue
            facts.append(fact)
        return tuple(facts)


def build_identity_index(
    snapshots: tuple[IdentitySnapshot, ...],
    events: tuple[IdentityAuditEvent, ...],
) -> IdentityIndex:
    snapshot_by_user = {item.user_id: item for item in snapshots}
    grouped: dict[tuple[str, str], list[IdentityAuditEvent]] = defaultdict(list)
    for event in events:
        if event.field_name not in SUPPORTED_FIELDS:
            raise IdentityError(f"unsupported audited identity field: {event.field_name}")
        if event.user_id not in snapshot_by_user:
            raise IdentityError(f"audit event references unknown user: {event.user_id}")
        grouped[(event.user_id, event.field_name)].append(event)

    facts: list[IdentifierFact] = []
    for snapshot in snapshots:
        facts.append(
            IdentifierFact(
                subject_id=snapshot.user_id,
                kind="user_id",
                normalized_value=normalize_identifier("user_id", snapshot.user_id),
                original_value=snapshot.user_id,
                available_at=snapshot.updated_at,
                source_id=snapshot.user_id,
                source_location=f"user_identities.csv#{snapshot.user_id}:user_id",
            )
        )
        for field in SUPPORTED_FIELDS:
            history = sorted(
                grouped.get((snapshot.user_id, field), ()),
                key=lambda item: (item.event_time, item.audit_id),
            )
            for earlier, later in zip(history, history[1:]):
                if normalize_identifier(field, earlier.new_value) != normalize_identifier(
                    field, later.old_value
                ):
                    raise IdentityError(
                        f"broken {field} audit chain for {snapshot.user_id}: "
                        f"{earlier.audit_id} -> {later.audit_id}"
                    )
            if history:
                first = history[0]
                facts.append(
                    IdentifierFact(
                        subject_id=snapshot.user_id,
                        kind=field,
                        normalized_value=normalize_identifier(field, first.old_value),
                        original_value=first.old_value,
                        valid_to=first.event_time,
                        available_at=first.event_time,
                        source_id=first.audit_id,
                        source_location=f"user_audit_log.csv#{first.audit_id}:old_value",
                    )
                )
                for index, event in enumerate(history):
                    valid_to = history[index + 1].event_time if index + 1 < len(history) else None
                    facts.append(
                        IdentifierFact(
                            subject_id=snapshot.user_id,
                            kind=field,
                            normalized_value=normalize_identifier(field, event.new_value),
                            original_value=event.new_value,
                            valid_from=event.event_time,
                            valid_to=valid_to,
                            available_at=event.event_time,
                            source_id=event.audit_id,
                            source_location=f"user_audit_log.csv#{event.audit_id}:new_value",
                        )
                    )
                current = getattr(snapshot, field)
                if normalize_identifier(field, history[-1].new_value) != normalize_identifier(
                    field, current
                ):
                    raise IdentityError(
                        f"current {field} disagrees with audit history for {snapshot.user_id}"
                    )
            else:
                current = getattr(snapshot, field)
                facts.append(
                    IdentifierFact(
                        subject_id=snapshot.user_id,
                        kind=field,
                        normalized_value=normalize_identifier(field, current),
                        original_value=current,
                        available_at=snapshot.updated_at,
                        source_id=snapshot.user_id,
                        source_location=f"user_identities.csv#{snapshot.user_id}:{field}",
                    )
                )

    deduplicated = {
        (
            fact.subject_id,
            fact.kind,
            fact.normalized_value,
            fact.valid_from,
            fact.valid_to,
            fact.source_id,
        ): fact
        for fact in facts
    }
    return IdentityIndex(tuple(deduplicated.values()))
