"""Build the submission archive from an explicit source allowlist."""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = (
    Path("code/evaluation/evaluation_report.md"),
    Path("code/evaluation/usage_report.md"),
)
ALLOWLIST = (
    Path("README.md"),
    Path(".gitignore"),
    Path(".env.example"),
    Path("code/main.py"),
    Path("code/package.py"),
    Path("code/requirements.txt"),
    Path("code/requirements-dev.txt"),
    Path("code/pytest.ini"),
    Path(".github/workflows/test.yml"),
)
TREES = (
    Path("code/erasecase"),
    Path("code/prompts"),
    Path("code/tests"),
    Path("code/evaluation"),
)
FORBIDDEN_PARTS = {".env", "dataset", "runs", "output.csv", ".venv", "venv", ".git"}


def package(output: Path, run_dir: Path, root: Path = ROOT) -> list[str]:
    """Write code.zip. The run directory is checked and never archived."""

    if output.suffix != ".zip":
        raise ValueError("package output must be a .zip file")
    if not run_dir.is_dir():
        raise ValueError("run directory must exist so the packager can exclude it")
    members = _members(root)
    resolved_run = run_dir.resolve()
    if any(_is_relative_to(path.resolve(), resolved_run) for path in members):
        raise ValueError("refusing to package the run directory")
    _reject_forbidden(members)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in members:
            data = path.read_bytes()
            _add(archive, path.relative_to(root).as_posix(), data)
            if path.relative_to(root) in REPORTS:
                archived = Path("evaluation") / path.name
                _add(archive, archived.as_posix(), data)
    names = _names(output)
    _assert_report_copies(output)
    if any(name.startswith("runs/") or name.startswith("dataset/") or name.endswith(".env") for name in names):
        raise ValueError("package contains a forbidden path")
    return names


def _members(root: Path) -> list[Path]:
    paths = [root / path for path in ALLOWLIST]
    for tree in TREES:
        base = root / tree
        paths.extend(
            path
            for path in base.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
        )
    missing = [path for path in paths if not path.is_file()]
    if missing:
        raise ValueError("required package file is missing: " + ", ".join(str(path) for path in missing))
    unique = sorted(set(paths), key=lambda path: path.relative_to(root).as_posix())
    return unique


def _reject_forbidden(paths: list[Path]) -> None:
    for path in paths:
        if path.name == ".env" or any(part in FORBIDDEN_PARTS for part in path.parts):
            raise ValueError(f"refusing to package {path}")


def _add(archive: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(filename=name, date_time=(2026, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, data)


def _names(output: Path) -> list[str]:
    with zipfile.ZipFile(output) as archive:
        return sorted(archive.namelist())


def _assert_report_copies(output: Path) -> None:
    with zipfile.ZipFile(output) as archive:
        for report in REPORTS:
            original = archive.read(report.as_posix())
            copy = archive.read(f"evaluation/{report.name}")
            if original != copy:
                raise ValueError(f"{report.name} archive copies differ")


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Package the EraseCase source allowlist.")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        names = package(args.output, args.run_dir)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"packed {len(names)} members into {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
