"""Frozen full-dataset audit, provenance check, and submission publish."""

from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import uuid
from pathlib import Path

from erasecase.audit import UnresolvedIntent, open_auditor
from erasecase.contracts import CONTRACT_VERSION, EvidenceFile
from erasecase.evidence import EvidenceError, _safe_path
from erasecase.identity import IdentityError
from erasecase.ingest import DatasetError, load_dataset
from erasecase.models import ProviderError
from erasecase.presentation import CommandFailure, render_csv
from erasecase.storage import RunStore
from erasecase.validators import (
    ValidationFailure,
    check_citation_provenance,
    parse_output_csv,
)

FINAL_BUDGET_USD = 4.0
CODE_PATHS = (
    "code/erasecase/audit.py",
    "code/erasecase/contracts.py",
    "code/erasecase/evidence.py",
    "code/erasecase/final_run.py",
    "code/erasecase/identity.py",
    "code/erasecase/ingest.py",
    "code/erasecase/planner.py",
    "code/erasecase/presentation.py",
    "code/erasecase/validators.py",
    "code/erasecase/vision.py",
)


def _read_vision(dataset_root: Path, repo_root: Path, budget_usd: float) -> None:
    """Read screenshots when a key and budget are available. Unread images stay unmarked."""

    from erasecase.models import has_openrouter_key
    from erasecase.vision import read_screenshots

    if budget_usd <= 0 or not has_openrouter_key():
        return
    try:
        manifest = read_screenshots(
            load_dataset(dataset_root).evidence_files,
            dataset_root,
            repo_root / "runs" / "vision",
            budget_usd=min(budget_usd, 0.75),
        )
    except ProviderError as exc:
        print(f"vision unresolved: {exc}", file=sys.stderr)
        return
    print(
        "vision complete "
        f"calls={manifest.get('calls')} cost_usd={manifest.get('cost_usd')} "
        f"files={len(manifest.get('files') or {})}"
    )


def _vision_usage(repo_root: Path) -> dict[str, object]:
    path = repo_root / "runs" / "vision" / "manifest.json"
    if not path.is_file():
        return {"calls": 0, "cost_usd": 0.0, "input_tokens": 0, "output_tokens": 0}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"calls": 0, "cost_usd": 0.0, "input_tokens": 0, "output_tokens": 0}
    return payload if isinstance(payload, dict) else {}


def prepare_run_dir(run_dir: Path, repo_root: Path) -> Path:
    if not str(run_dir).strip():
        raise CommandFailure(2, "RUN_INPUT", "run requires --run-dir under runs/ or outside the repository")
    resolved = run_dir.expanduser().resolve()
    root = repo_root.resolve()
    dataset = (root / "dataset").resolve()
    runs = root / "runs"
    inside_repo = resolved == root or root in resolved.parents
    outside_runs = inside_repo and resolved != runs and runs not in resolved.parents
    if (
        resolved == root
        or resolved.name == "output.csv"
        or resolved == dataset
        or dataset in resolved.parents
        or resolved in root.parents
        or outside_runs
    ):
        raise CommandFailure(
            2,
            "RUN_INPUT",
            f"{resolved} is not an isolated run directory; use runs/final or a directory outside the repository",
        )
    if resolved.exists() and not resolved.is_dir():
        raise CommandFailure(2, "RUN_INPUT", f"{resolved} is a file; pass a directory such as runs/final")
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def code_fingerprint(repo_root: Path) -> str:
    digest = hashlib.sha256()
    for relative in CODE_PATHS:
        path = repo_root / relative
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def output_fingerprint(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def evidence_fingerprint(records: list[dict[str, object]]) -> str:
    lines = [
        f"{item['evidence_id']}:{item['sha256']}"
        for item in sorted(records, key=lambda item: str(item["evidence_id"]))
    ]
    return hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()


def publish_output(text: str, output_path: Path) -> None:
    """Replace a submission only after the candidate has already been validated."""

    if output_path.is_symlink():
        raise ValidationFailure("refusing to replace a symlinked submission")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_name(f".{output_path.name}.{os.getpid()}.partial")
    if temporary.is_symlink():
        raise ValidationFailure("refusing to publish through a symlink")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, output_path)


def _file_records(catalog) -> list[dict[str, object]]:
    return [
        {
            "evidence_id": item.evidence_id,
            "file_path": item.file_path,
            "origin": item.origin,
            "captured_at": item.captured_at.isoformat(),
            "sha256": item.sha256,
            "byte_count": item.byte_count,
            "status": item.status.value,
        }
        for item in sorted(catalog.extractions, key=lambda item: item.evidence_id)
    ]


def _read_manifest(run_dir: Path) -> dict[str, object]:
    path = run_dir / "manifest.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationFailure("run manifest is missing or unreadable") from exc
    if not isinstance(payload, dict):
        raise ValidationFailure("run manifest must be an object")
    return payload


def verify_recorded_files(dataset_root: Path, records: object) -> str:
    if not isinstance(records, list) or not records:
        raise ValidationFailure("run manifest is missing evidence fingerprints")
    checked: list[dict[str, object]] = []
    for item in records:
        if not isinstance(item, dict):
            raise ValidationFailure("evidence fingerprint record is malformed")
        try:
            entry = EvidenceFile.model_validate(
                {
                    "file_id": item["evidence_id"],
                    "file_path": item["file_path"],
                    "origin": item["origin"],
                    "captured_at": item["captured_at"],
                }
            )
            expected_hash = str(item["sha256"])
            expected_size = int(item["byte_count"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValidationFailure("evidence fingerprint record is malformed") from exc
        try:
            path = _safe_path(dataset_root, entry)
            data = path.read_bytes()
        except EvidenceError as exc:
            raise ValidationFailure(f"{entry.file_id} failed the evidence path check") from exc
        actual_hash = hashlib.sha256(data).hexdigest()
        if len(data) != expected_size or actual_hash != expected_hash:
            raise ValidationFailure(f"{entry.file_id} fingerprint does not match the recorded file")
        checked.append(item)
    return evidence_fingerprint(checked)


def _provenance(text: str, bundle) -> None:
    cases = parse_output_csv(
        text,
        expected_ids=tuple(request.case_id for request in bundle.requests),
    )
    check_citation_provenance(
        cases,
        bundle.requests,
        bundle.evidence_files,
        bundle.activities,
        bundle.identity_events,
    )


def validate_submission(dataset_root: Path, input_path: Path, run_dir: Path, repo_root: Path) -> int:
    try:
        bundle = load_dataset(dataset_root)
        text = input_path.read_text(encoding="utf-8")
        _provenance(text, bundle)
        manifest = _read_manifest(run_dir)
        recorded_output = str(manifest.get("output_sha256", ""))
        actual_output = output_fingerprint(text)
        if not recorded_output or actual_output != recorded_output:
            raise ValidationFailure("output fingerprint does not match the run manifest")
        recorded_evidence = str(manifest.get("evidence_fingerprint", ""))
        actual_evidence = verify_recorded_files(dataset_root, manifest.get("files"))
        if actual_evidence != recorded_evidence:
            raise ValidationFailure("evidence fingerprint does not match the run manifest")
        if str(manifest.get("code_fingerprint", "")) != code_fingerprint(repo_root):
            raise ValidationFailure("code fingerprint does not match the run manifest")
        candidate = (run_dir / "candidate.csv").read_text(encoding="utf-8")
        if output_fingerprint(candidate) != actual_output:
            raise ValidationFailure("candidate.csv does not match output.csv")
    except ValidationFailure as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        return 3
    except (DatasetError, OSError) as exc:
        print(f"validation unresolved: {exc.__class__.__name__}", file=sys.stderr)
        return 4
    rows = int(manifest.get("rows", 0))
    print(
        "validation passed "
        f"rows={rows} output_sha256={actual_output} evidence_fingerprint={actual_evidence}"
    )
    return 0


def _resume(resume_id: str, dataset_root: Path, run_dir: Path, output_path: Path, repo_root: Path) -> int:
    try:
        manifest = _read_manifest(run_dir)
    except ValidationFailure as exc:
        print(f"resume unresolved: {exc}", file=sys.stderr)
        return 4
    if manifest.get("run_id") != resume_id:
        print("resume unresolved: run id does not match the manifest", file=sys.stderr)
        return 4
    if manifest.get("model_calls") != 0:
        print("resume unresolved: cached run recorded model calls", file=sys.stderr)
        return 4
    try:
        if str(manifest.get("code_fingerprint", "")) != code_fingerprint(repo_root):
            raise ValidationFailure("code fingerprint does not match the cached run")
        actual_evidence = verify_recorded_files(dataset_root, manifest.get("files"))
        if actual_evidence != manifest.get("evidence_fingerprint"):
            raise ValidationFailure("evidence fingerprint does not match the cached run")
        candidate_path = run_dir / "candidate.csv"
        text = candidate_path.read_text(encoding="utf-8")
        if output_fingerprint(text) != manifest.get("output_sha256"):
            raise ValidationFailure("candidate fingerprint does not match the cached run")
        bundle = load_dataset(dataset_root)
        _provenance(text, bundle)
        current = output_path.read_text(encoding="utf-8") if output_path.is_file() else ""
        if output_fingerprint(current) != manifest.get("output_sha256"):
            publish_output(text, output_path)
    except (ValidationFailure, DatasetError, OSError, KeyError, TypeError) as exc:
        print(f"resume unresolved: {exc.__class__.__name__}", file=sys.stderr)
        return 4
    print(f"resumed run_id={resume_id} output_sha256={manifest.get('output_sha256')}")
    return 0


def execute_final_run(
    *,
    dataset_root: Path,
    run_dir: Path,
    output_path: Path,
    budget_usd: float,
    resume_id: str | None,
    repo_root: Path,
) -> int:
    if budget_usd < 0 or budget_usd > FINAL_BUDGET_USD:
        print("final-run budget must be from 0 through 4", file=sys.stderr)
        return 2
    try:
        isolated = prepare_run_dir(run_dir, repo_root)
    except CommandFailure as exc:
        print(exc.render(), file=sys.stderr)
        return exc.exit_code
    if resume_id:
        return _resume(resume_id, dataset_root, isolated, output_path, repo_root)

    started = time.perf_counter()
    try:
        _read_vision(dataset_root, repo_root, budget_usd)
        auditor, bundle = open_auditor(dataset_root)
        cases = []
        unresolved = 0
        for request in bundle.requests:
            try:
                cases.append(auditor.assess(request).case)
            except UnresolvedIntent:
                unresolved += 1
        if unresolved:
            print(f"run unresolved: unresolved_intents={unresolved}", file=sys.stderr)
            return 4
        text = render_csv(tuple(cases))
        _provenance(text, bundle)
    except (DatasetError, EvidenceError, IdentityError, ValidationFailure, UnresolvedIntent) as exc:
        print(f"run unresolved: {exc.__class__.__name__}", file=sys.stderr)
        return 4

    records = _file_records(auditor.evidence.catalog)
    file_digest = evidence_fingerprint(records)
    submission_digest = output_fingerprint(text)
    elapsed = round(time.perf_counter() - started, 2)
    counts: dict[str, int] = {}
    for case in cases:
        counts[case.deletion_status.value] = counts.get(case.deletion_status.value, 0) + 1
    vision = _vision_usage(repo_root)
    vision_calls = int(vision.get("calls") or 0)
    vision_cost = float(vision.get("cost_usd") or 0)
    input_tokens = int(vision.get("input_tokens") or 0)
    output_tokens = int(vision.get("output_tokens") or 0)
    manifest = {
        "run_id": uuid.uuid4().hex,
        "contract_version": CONTRACT_VERSION,
        "rows": len(cases),
        "status_counts": counts,
        "model_calls": vision_calls,
        "attempts": vision_calls,
        "cache_hits": 0,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cost_usd": vision_cost,
        "budget_usd": budget_usd,
        "vision_required": sum(1 for item in records if item["status"] == "VISION_REQUIRED"),
        "vision_calls": vision_calls,
        "elapsed_seconds": elapsed,
        "output_sha256": submission_digest,
        "evidence_fingerprint": file_digest,
        "code_fingerprint": code_fingerprint(repo_root),
        "files": records,
    }
    (isolated / "candidate.csv").write_text(text, encoding="utf-8")
    (isolated / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    with RunStore(isolated / "state.sqlite") as store:
        catalog = auditor.evidence.catalog
        store.record_evidence(catalog.extractions, catalog.observations, catalog.links)
        store.record_identifier_facts(auditor.identity.facts)
    publish_output(text, output_path)
    print(
        "final run complete "
        f"run_id={manifest['run_id']} rows={manifest['rows']} "
        f"statuses={json.dumps(counts, sort_keys=True)} "
        f"model_calls={vision_calls} cost_usd={vision_cost} output_sha256={submission_digest} "
        f"evidence_fingerprint={file_digest} vision_required={manifest['vision_required']} "
        f"elapsed_seconds={elapsed}"
    )
    return 0
