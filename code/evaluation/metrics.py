"""Step and status metrics for public and custom deletion audits.

Empty expected and actual sequences contribute a sequence hit and a full-row
hit when the status also matches. They add nothing to positional or multiset
ratios, because the maximum sequence length is zero. A one-sided empty
sequence is a sequence miss: every step on the longer side is a false positive
or a false negative, and each of its seven fields counts as a positional miss.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

StepTuple = tuple[object, ...]

EMPTY_CONVENTION = (
    "Both-empty sequences are exact sequence matches and do not change "
    "positional or multiset ratios. A one-sided empty sequence mismatches."
)


@dataclass(frozen=True)
class SuiteMetrics:
    """Aggregate scores for one labeled suite."""

    cases: int
    status_hits: int
    sequence_hits: int
    full_row_hits: int
    positional_exact_steps: int
    positional_step_slots: int
    positional_fields: int
    positional_field_slots: int
    true_positives: int
    false_positives: int
    false_negatives: int

    @property
    def status_accuracy(self) -> float:
        return _ratio(self.status_hits, self.cases)

    @property
    def sequence_accuracy(self) -> float:
        return _ratio(self.sequence_hits, self.cases)

    @property
    def full_row_accuracy(self) -> float:
        return _ratio(self.full_row_hits, self.cases)

    @property
    def positional_step_accuracy(self) -> float:
        return _ratio(self.positional_exact_steps, self.positional_step_slots)

    @property
    def field_accuracy(self) -> float:
        return _ratio(self.positional_fields, self.positional_field_slots)

    @property
    def precision(self) -> float:
        return _ratio(self.true_positives, self.true_positives + self.false_positives)

    @property
    def recall(self) -> float:
        return _ratio(self.true_positives, self.true_positives + self.false_negatives)

    @property
    def f1(self) -> float:
        precision = self.precision
        recall = self.recall
        return _ratio(2 * precision * recall, precision + recall)


def score_case(
    *,
    actual_status: str,
    expected_status: str,
    actual_steps: tuple[StepTuple, ...],
    expected_steps: tuple[StepTuple, ...],
) -> SuiteMetrics:
    """Score one case. Step tuples are the seven output fields, in order."""

    status_hit = actual_status == expected_status
    sequence_hit = actual_steps == expected_steps
    width = max(len(actual_steps), len(expected_steps))
    exact_steps = 0
    matched_fields = 0
    for index in range(width):
        actual = actual_steps[index] if index < len(actual_steps) else None
        expected = expected_steps[index] if index < len(expected_steps) else None
        if actual is not None and actual == expected:
            exact_steps += 1
            matched_fields += 7
        elif actual is not None and expected is not None:
            matched_fields += sum(left == right for left, right in zip(actual, expected, strict=True))
    true_positives, false_positives, false_negatives = _multiset(
        _without_step_no(actual_steps), _without_step_no(expected_steps)
    )
    return SuiteMetrics(
        cases=1,
        status_hits=int(status_hit),
        sequence_hits=int(sequence_hit),
        full_row_hits=int(status_hit and sequence_hit),
        positional_exact_steps=exact_steps,
        positional_step_slots=width,
        positional_fields=matched_fields,
        positional_field_slots=7 * width,
        true_positives=true_positives,
        false_positives=false_positives,
        false_negatives=false_negatives,
    )


def combine(metrics: tuple[SuiteMetrics, ...]) -> SuiteMetrics:
    """Sum case metrics. Precision and recall stay micro-averaged."""

    if not metrics:
        return SuiteMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    return SuiteMetrics(
        cases=sum(item.cases for item in metrics),
        status_hits=sum(item.status_hits for item in metrics),
        sequence_hits=sum(item.sequence_hits for item in metrics),
        full_row_hits=sum(item.full_row_hits for item in metrics),
        positional_exact_steps=sum(item.positional_exact_steps for item in metrics),
        positional_step_slots=sum(item.positional_step_slots for item in metrics),
        positional_fields=sum(item.positional_fields for item in metrics),
        positional_field_slots=sum(item.positional_field_slots for item in metrics),
        true_positives=sum(item.true_positives for item in metrics),
        false_positives=sum(item.false_positives for item in metrics),
        false_negatives=sum(item.false_negatives for item in metrics),
    )


def _without_step_no(steps: tuple[StepTuple, ...]) -> tuple[StepTuple, ...]:
    return tuple(step[1:] for step in steps)


def _multiset(
    actual: tuple[StepTuple, ...], expected: tuple[StepTuple, ...]
) -> tuple[int, int, int]:
    actual_counts = Counter(actual)
    expected_counts = Counter(expected)
    true_positives = sum(
        min(actual_counts[key], expected_counts[key])
        for key in actual_counts.keys() | expected_counts.keys()
    )
    false_positives = sum(actual_counts.values()) - true_positives
    false_negatives = sum(expected_counts.values()) - true_positives
    return true_positives, false_positives, false_negatives


def _ratio(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 1.0
    return numerator / denominator
