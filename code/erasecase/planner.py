"""Ordered deletion-plan steps. Models do not choose operations or sequence."""

from __future__ import annotations

from dataclasses import dataclass

from .contracts import STEP_RULES, Operation, OutputStep, Phase

OPERATION_ORDER: tuple[Operation, ...] = (
    Operation.REPORT_REMAINING_RECORD,
    Operation.REPORT_EXPOSED_PII,
    Operation.REPORT_ACTIVE_DATA_FLOW,
    Operation.REPORT_RESTORE_RISK,
    Operation.DISABLE_DATA_FLOW,
    Operation.BLOCK_RESTORE,
    Operation.DELETE_RECORD,
    Operation.REDACT_RECORD,
    Operation.ANONYMIZE_RECORD,
    Operation.VERIFY_RECORD_ABSENT,
    Operation.VERIFY_RECORD_PRESENT,
    Operation.VERIFY_RECORD_REDACTED,
    Operation.VERIFY_RECORD_ANONYMIZED,
    Operation.VERIFY_DATA_FLOW_DISABLED,
    Operation.VERIFY_RESTORE_BLOCKED,
)

_ORDER = {operation: index for index, operation in enumerate(OPERATION_ORDER)}
_PHASE = {Phase.FINDING: 0, Phase.REMEDIATION: 1, Phase.VERIFICATION: 2}


@dataclass(frozen=True)
class Treatment:
    """One resource's required finding, repair, and check."""

    system_id: str
    resource_id: str
    evidence_id: str
    verification: Operation
    finding: Operation | None = None
    remediation: Operation | None = None

    @property
    def compliant(self) -> bool:
        return self.finding is None


def build_steps(treatments: tuple[Treatment, ...], *, complete: bool) -> tuple[OutputStep, ...]:
    """Number steps after phase, operation, system, and resource ordering."""

    drafted: list[tuple[int, int, str, str, OutputStep]] = []
    for treatment in treatments:
        operations: list[tuple[Operation, str]] = []
        if treatment.finding is not None and treatment.remediation is not None:
            operations.append((treatment.finding, treatment.evidence_id))
            operations.append((treatment.remediation, ""))
            operations.append((treatment.verification, ""))
        elif complete and treatment.compliant:
            operations.append((treatment.verification, treatment.evidence_id))
        elif treatment.compliant:
            operations.append((treatment.verification, ""))
        else:
            raise ValueError("a violation requires both a finding and a remediation")
        for operation, evidence_id in operations:
            phase, state = STEP_RULES[operation]
            step = OutputStep(
                step_no=1,
                phase=phase,
                system_id=treatment.system_id,
                resource_id=treatment.resource_id,
                operation=operation,
                state=state,
                evidence_id=evidence_id,
            )
            drafted.append(
                (_PHASE[phase], _ORDER[operation], treatment.system_id, treatment.resource_id, step)
            )
    drafted.sort(key=lambda item: item[:4])
    return tuple(
        step.model_copy(update={"step_no": index})
        for index, (*_, step) in enumerate(drafted, start=1)
    )
