"""Archive allowlist, report copies, and secret exclusion."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from package import package

ROOT = Path(__file__).resolve().parents[2]


def test_package_allowlist_excludes_secrets_and_duplicates_reports(tmp_path: Path) -> None:
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "secret.txt").write_text("do-not-pack", encoding="utf-8")
    output = tmp_path / "code.zip"
    names = package(output, run_dir, ROOT)
    assert "README.md" in names
    assert "code/evaluation/evaluation_report.md" in names
    assert "evaluation/evaluation_report.md" in names
    assert "code/evaluation/usage_report.md" in names
    assert "evaluation/usage_report.md" in names
    assert ".env.example" in names
    assert ".gitignore" in names
    assert not any(name == ".env" or name.startswith("dataset/") or name.startswith("runs/") for name in names)
    assert not any(name.endswith(".zip") and name != "code.zip" for name in names)
    with zipfile.ZipFile(output) as archive:
        assert archive.read("code/evaluation/evaluation_report.md") == archive.read(
            "evaluation/evaluation_report.md"
        )
        assert b"OPENROUTER_API_KEY=replace-with-local-key" in archive.read(".env.example")
        assert b"do-not-pack" not in archive.read("README.md")
        bundled = b"\n".join(archive.read(name) for name in archive.namelist())
        assert b"sk-" + b"or-" not in bundled
        assert b"BEGIN " + b"PRIVATE KEY" not in bundled
        assert b"BEGIN " + b"OPENSSH PRIVATE KEY" not in bundled


def test_package_rejects_a_missing_run_directory(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        package(tmp_path / "code.zip", tmp_path / "missing", ROOT)
