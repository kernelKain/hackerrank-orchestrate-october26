# EraseCase

EraseCase is the deletion-audit agent for HackerRank Orchestrate October 2026,
Ghost Data Still Exists. It reads the participant files under `dataset/`,
decides whether each request authorizes deletion, and writes one row per case
to root `output.csv`.

## Setup

Python 3.12 or newer is required. The verified local runtime is Python 3.14.
`pdftotext` and `pdftoppm` must be on `PATH`. SQLite is the one bundled with
Python.

From the repository root:

```text
python3 -m venv .venv
.venv/bin/python -m pip install -r code/requirements-dev.txt
.venv/bin/python code/main.py preflight
```

On Windows, use the virtual environment's `Scripts\python.exe`.

Copy `.env.example` to `.env` only for an online screenshot reading, and put
the OpenRouter key in that local file. The program loads `.env` without
replacing variables that are already set. `.env` is not part of this archive.

## Run

From the repository root, with the virtual environment active:

```text
.venv/bin/python code/main.py run --run-dir runs/final --budget-usd 4
.venv/bin/python code/main.py validate --input output.csv --run-dir runs/final
```

`run` writes `output.csv` with the columns `case_id`, `deletion_status`, and
`steps_json`. It must contain one row for every case in
`dataset/deletion_requests.csv`, sorted by `case_id`. A request that does not
authorize deletion is `NOT_APPLICABLE` and its steps are `[]`.

Offline checks:

```text
PYTHONPATH=code .venv/bin/python -m pytest -c code/pytest.ini code/tests
PYTHONPATH=code .venv/bin/python -m evaluation.main --suite all --run-dir runs/evaluation --budget-usd 0
```

## Approach

The audit is deterministic. The model does not choose the deletion status, the
operations, their order, or the CSV.

1. Read the request text and accept a deletion only when the text asks for one.
   Access, correction, export, and marketing opt-out requests are
   `NOT_APPLICABLE`.
2. Resolve the person's current and historical email, phone, user id, and email
   hash from the identity snapshot and the audit log. Only values known at or
   before `audit_at` are used.
3. Read logs, JSON, text, SQL snapshots, and PDFs. A row belongs to the person
   only when it carries one of those identifiers. If one trace contains exactly
   one such identifier, that value is copied onto the other lines of the same
   trace. A trace with two different values is left alone. A deletion-activity
   row cannot create a step by itself, and workflow success is not treated as
   proof.
4. Read each screenshot with `google/gemini-3.8-flash`. A visible record is kept
   only when the screen shows both a resource id and a strong identifier.
   Otherwise the screen is ignored.
5. Apply `deletion_rules.csv`. Records that policy says to retain, redact,
   anonymize, or keep as a tombstone are not deleted. A tombstone keeps the
   stable user reference and drops the direct identifiers.
6. Report every remaining violation and every active copy or restore path that
   the evidence supports. Stop those paths before changing the records they can
   recreate. Verification then checks the required final state.

Findings cite the evidence file, activity, or audit row that proves them.
Remediation and the checks that follow it use an empty evidence id, because
that work has not happened yet. A complete case contains only verification
steps, each citing evidence from at or before `audit_at`.

Public sample labels are used only by the separate evaluation scorer. They are
not imported by the auditor.
