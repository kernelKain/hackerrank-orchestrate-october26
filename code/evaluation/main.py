"""Run offline public and custom evaluation without writing output.csv."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from erasecase.models import ROOT

from .metrics import EMPTY_CONVENTION
from .scoring import score_custom, score_public


def evaluate(suite: str, run_dir: Path) -> int:
    if suite not in {"public", "custom", "all"}:
        print("suite must be public, custom, or all", file=sys.stderr)
        return 2
    run_dir.mkdir(parents=True, exist_ok=True)
    payload: dict[str, object] = {"empty_convention": EMPTY_CONVENTION, "model_calls": 0}
    if suite in {"public", "all"}:
        public = score_public(ROOT / "dataset")
        payload["public"] = _metrics_payload(public.metrics)
        payload["public_categories"] = dict(public.categories)
        payload["public_cases"] = [
            {
                "case_id": case.case_id,
                "expected_status": case.expected_status,
                "actual_status": case.actual_status,
                "sequence_match": case.sequence_match,
                "category": case.category,
            }
            for case in public.cases
        ]
    if suite in {"custom", "all"}:
        custom, cases = score_custom(ROOT / "dataset")
        payload["custom"] = _metrics_payload(custom)
        payload["custom_cases"] = [
            {
                "case_id": case.case_id,
                "summary": case.summary,
                "status": case.assessment.deletion_status.value,
                "expected_status": case.expected_status,
                "independent_expectation": case.independent_expectation,
                "rationale": case.rationale,
            }
            for case in cases
        ]
    destination = run_dir / "metrics.json"
    destination.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {destination}")
    print("model_calls=0")
    return 0


def _metrics_payload(metrics) -> dict[str, object]:
    return {
        "cases": metrics.cases,
        "status_hits": metrics.status_hits,
        "sequence_hits": metrics.sequence_hits,
        "full_row_hits": metrics.full_row_hits,
        "positional_exact_steps": metrics.positional_exact_steps,
        "positional_step_slots": metrics.positional_step_slots,
        "positional_fields": metrics.positional_fields,
        "positional_field_slots": metrics.positional_field_slots,
        "true_positives": metrics.true_positives,
        "false_positives": metrics.false_positives,
        "false_negatives": metrics.false_negatives,
        "status_accuracy": metrics.status_accuracy,
        "sequence_accuracy": metrics.sequence_accuracy,
        "full_row_accuracy": metrics.full_row_accuracy,
        "positional_step_accuracy": metrics.positional_step_accuracy,
        "field_accuracy": metrics.field_accuracy,
        "precision": metrics.precision,
        "recall": metrics.recall,
        "f1": metrics.f1,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Score EraseCase without reading organizer-only files.")
    parser.add_argument("--suite", default="all", choices=("public", "custom", "all"))
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--budget-usd", type=float, default=0.75)
    args = parser.parse_args(argv)
    if args.budget_usd < 0 or args.budget_usd > 0.75:
        print("evaluation budget must be from 0 through 0.75", file=sys.stderr)
        return 2
    return evaluate(args.suite, args.run_dir)


if __name__ == "__main__":
    raise SystemExit(main())
