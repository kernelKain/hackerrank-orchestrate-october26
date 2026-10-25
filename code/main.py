"""EraseCase command-line entry point."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from pathlib import Path
from typing import Sequence

from erasecase.contracts import CONTRACT_VERSION
from erasecase.fixtures import SCENARIOS, run_fixture_review
from erasecase.models import (
    ROOT,
    SEMANTIC_CANDIDATES,
    VISION_CANDIDATE,
    OpenRouterClient,
    ProviderError,
    estimate_probe_cost,
    has_openrouter_key,
    synthetic_probe_image,
)
from erasecase.presentation import CommandFailure, format_check

EXIT_OK = 0
EXIT_SOFTWARE = 1
EXIT_USAGE = 2
EXIT_VALIDATION = 3
EXIT_UNRESOLVED = 4


def _dataset_checks() -> list[tuple[str, bool, str]]:
    dataset = ROOT / "dataset"
    required = {
        "deletion_requests.csv": 518,
        "sample_deletion_requests.csv": 32,
        "evidence_files.csv": 94,
    }
    checks: list[tuple[str, bool, str]] = []
    for name, expected_rows in required.items():
        path = dataset / name
        try:
            with path.open(newline="", encoding="utf-8") as handle:
                count = sum(1 for _ in csv.DictReader(handle))
            checks.append((name, count == expected_rows, f"{count} data rows"))
        except OSError as exc:
            checks.append((name, False, exc.__class__.__name__))
    evidence_dir = dataset / "evidence"
    checks.append(("evidence directory", evidence_dir.is_dir(), str(evidence_dir)))
    return checks


def preflight(*, online: bool) -> int:
    checks = _dataset_checks()
    checks.extend(
        [
            ("Python >= 3.12", sys.version_info >= (3, 12), sys.version.split()[0]),
            ("pdftotext", shutil.which("pdftotext") is not None, shutil.which("pdftotext") or "missing"),
            ("pdftoppm", shutil.which("pdftoppm") is not None, shutil.which("pdftoppm") or "missing"),
            ("contract version", True, CONTRACT_VERSION),
            ("root .env ignored", _is_ignored(ROOT / ".env"), "git check-ignore"),
        ]
    )
    key_present = has_openrouter_key()
    if online:
        checks.append(("OpenRouter key configured", key_present, "present" if key_present else "not configured"))
    if online and key_present:
        try:
            client = OpenRouterClient()
            metadata = client.current_key_metadata().get("data")
            models = {item.get("id") for item in client.models()}
            checks.append(("OpenRouter authentication", isinstance(metadata, dict), "authenticated"))
            for model in (*SEMANTIC_CANDIDATES, VISION_CANDIDATE):
                checks.append((f"model {model}", model in models, "available" if model in models else "unavailable"))
        except ProviderError as exc:
            checks.append(("OpenRouter online check", False, str(exc)))
    elif online:
        checks.append(("OpenRouter online check", False, "configure OPENROUTER_API_KEY first"))

    print("EraseCase preflight")
    for label, ok, detail in checks:
        print(format_check(label, ok, detail))
    if not online:
        print("[SKIP] OpenRouter access: use preflight --online when credentials are configured")
    required_failures = [label for label, ok, _ in checks if not ok]
    return EXIT_OK if not required_failures else EXIT_UNRESOLVED


def _is_ignored(path: Path) -> bool:
    import subprocess

    result = subprocess.run(
        ["git", "check-ignore", "--quiet", str(path)],
        cwd=ROOT,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0


def probe(*, budget_usd: float) -> int:
    if budget_usd <= 0 or budget_usd > 0.25:
        print("probe budget must be greater than 0 and at most $0.25", file=sys.stderr)
        return EXIT_USAGE
    try:
        client = OpenRouterClient()
        catalog = {item.get("id"): item for item in client.models()}
        missing = [model for model in (*SEMANTIC_CANDIDATES, VISION_CANDIDATE) if model not in catalog]
        if missing:
            raise ProviderError("required probe models unavailable: " + ", ".join(missing))
        reserved = {
            SEMANTIC_CANDIDATES[0]: estimate_probe_cost(
                catalog[SEMANTIC_CANDIDATES[0]], input_tokens=2_048, output_tokens=256
            ),
            VISION_CANDIDATE: estimate_probe_cost(
                catalog[VISION_CANDIDATE], input_tokens=2_048, output_tokens=256, images=1
            ),
        }
        reserved_total = sum(reserved.values())
        if reserved_total > budget_usd:
            raise ProviderError(
                f"catalog-priced reservation ${reserved_total:.6f} exceeds probe budget"
            )
        semantic = client.structured_probe(
            model=SEMANTIC_CANDIDATES[0],
            prompt="Return the exact string DELETE in the value field.",
        )
        vision = client.structured_probe(
            model=VISION_CANDIDATE,
            prompt="Read the synthetic image and return its exact text in the value field.",
            image_data_url=synthetic_probe_image(),
        )
    except ProviderError as exc:
        print(f"probe unresolved: {exc}", file=sys.stderr)
        return EXIT_UNRESOLVED
    results = [semantic, vision]
    known_costs = [item.cost_usd for item in results if item.cost_usd is not None]
    if len(known_costs) != len(results):
        print("probe unresolved: provider omitted one or more cost fields", file=sys.stderr)
        return EXIT_UNRESOLVED
    total = sum(known_costs)
    if total > budget_usd:
        print("probe exceeded its approved budget; stop all paid work", file=sys.stderr)
        return EXIT_UNRESOLVED
    for item in results:
        print(
            json.dumps(
                {
                    "model": item.model,
                    "returned_model": item.returned_model,
                    "provider": item.provider,
                    "input_tokens": item.input_tokens,
                    "output_tokens": item.output_tokens,
                    "cost_usd": item.cost_usd,
                    "reserved_cost_usd": reserved[item.model],
                    "latency_ms": item.latency_ms,
                    "contract_value": item.value,
                },
                sort_keys=True,
            )
        )
    print(f"probe_total_cost_usd={total:.6f}")
    return EXIT_OK


def pending(command: str) -> int:
    print(f"{command} is reserved for a later approved implementation unit", file=sys.stderr)
    return EXIT_UNRESOLVED


def fixtures_command(run_dir: str, scenario: str) -> int:
    try:
        review = run_fixture_review(Path(run_dir), ROOT, scenario)
    except CommandFailure as exc:
        print(exc.render(), file=sys.stderr)
        return exc.exit_code
    for line in review.lines:
        print(line)
    return EXIT_OK


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        prog="erasecase",
        description="Evidence-grounded personal-data deletion auditor.",
        epilog=(
            "fixtures publishes a labeled synthetic review under --run-dir.\n"
            "It does not read evaluation requests, call a provider, or write output.csv.\n"
            "Exit codes: 0 finished; 1 software failure; 2 usage or configuration;\n"
            "3 validation failure; 4 unresolved evidence, provider, or budget;\n"
            "130 keyboard interruption. Ctrl+C prints interrupted and does not\n"
            "replace a previously valid submission."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subcommands = result.add_subparsers(dest="command")
    preflight_parser = subcommands.add_parser("preflight", help="check local or online prerequisites")
    preflight_parser.add_argument("--online", action="store_true", help="authenticate and check approved model IDs")
    probe_parser = subcommands.add_parser("probe", help="run bounded schema and vision access probes")
    probe_parser.add_argument("--budget-usd", type=float, default=0.25)
    fixtures_parser = subcommands.add_parser(
        "fixtures",
        help="publish a labeled synthetic review without writing output.csv",
    )
    fixtures_parser.add_argument(
        "--run-dir",
        required=True,
        help="isolated directory under runs/ or outside the repository",
    )
    fixtures_parser.add_argument(
        "--scenario",
        default="success",
        choices=SCENARIOS,
        help="success, or empty, malformed, budget, partial, missing-input, interrupt",
    )
    for name in ("run", "validate"):
        subcommands.add_parser(name, help=f"{name} (implemented in a later unit)")
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command is None:
        return pending("full evaluation run")
    if args.command == "preflight":
        return preflight(online=args.online)
    if args.command == "probe":
        return probe(budget_usd=args.budget_usd)
    if args.command == "fixtures":
        return fixtures_command(args.run_dir, args.scenario)
    return pending(args.command)


def run(argv: Sequence[str] | None = None) -> int:
    try:
        return main(argv)
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(run())
