# EraseCase

**Every deletion, accounted for.**

EraseCase is the planned deletion-audit agent for HackerRank Orchestrate October
2026: **Ghost Data Still Exists**. It reconstructs evidence at each request's
audit cutoff and produces the required findings, remediation and verification.

## Current status

**Prompt 1 is complete. E01 is implemented and verified; E02 awaits A1 authorization.**

The canonical plan is docs/ENGINEERING_BLUEPRINT.md, version 1.3. It contains the
complete specification, execution directive and readiness manifest. E01 established
the application foundation, protected local configuration, strict contracts,
preflight checks, OpenRouter boundaries, persistent run state and offline tests.
Fixture UX, audit logic, evaluation, the final run and packaging remain unfinished.

| Document | Purpose |
| --- | --- |
| [Approved engineering blueprint](docs/ENGINEERING_BLUEPRINT.md) | Complete specification, directive, step/tool map and readiness manifest |
| [Product blueprint](docs/PRODUCT_BLUEPRINT.md) | Approved product boundary and amendments |
| [Execution state](docs/EXECUTION_STATE.md) | Current unit, checks, commits, budget and tool handovers |
| [AGENTS.md](AGENTS.md) | Mandatory instructions and shared logging contract |
| [Problem statement](problem_statement.md) | Challenge input/output and policy contract |
| [Trace instructions](agent_trace_instructions.md) | Relevant session-export requirements |

## Approved build workflow

The user authorizes one outcome at a time under A1. Work is committed and pushed
directly to `main`, with a separate commit after each verified step. Do not create
implementation or phase branches, and do not group multiple step outcomes into
one commit.

| Step | Outcome | Tool |
| --- | --- | --- |
| E01 | Foundation, protected configuration, contracts and access proof | Codex |
| E02 | Fixture CLI/report journey and mandatory UX approval | Cursor |
| E03 | Evidence, historical identity and provenance | Codex |
| E04 | Audit state, policy, challenge checks and ordered resolution | Codex |
| E05 | Evaluation, debugging, safety and release tooling | Codex |
| E06 | Final 518-case run and reconciled reports | Codex |
| E07 | Documentation polish, then final technical inspection | Cursor, then Codex |

At every step boundary, record the commit, verification, remaining budget and
whether to stay in Codex or switch tools. Both tools use the same checkout,
root log.txt and execution notes. Only one edits at a time.
Codex owns important engineering and correctness; Cursor handles presentation and
documentation. No web frontend, dashboard, deployment, video or presentation is
part of the approved scope.

Working target: build and submit by **25 October 2026, 5 PM IST**. The user plans
the interview after 6 PM and manages the actual portal/interview deadlines.
This working target is not a verified official cutoff.

## Planned setup and local credentials

Future runtime: Python 3.12–3.14, requests, Pydantic, Pillow, python-dotenv, SQLite
and Poppler utilities. Pytest and offline CI protect the core contracts.
Exact dependency pins and installation proofs belong to E01.

E01 must create and verify .gitignore exclusions before local secret entry.
The project will load the root .env explicitly without overriding existing
environment values. Credentials are then read from environment variables.

Only a placeholder .env.example may be committed. Actual .env files and secret
variants must be ignored, untracked, absent from logs and excluded independently
from code.zip. Do not paste the OpenRouter key into chat.

These E01 setup and preflight commands have been executed and verified locally:

    python3 -m venv .venv
    .venv/bin/python -m pip install -r code/requirements-dev.txt
    .venv/bin/python code/main.py preflight

Windows uses the virtual environment's Scripts/python.exe equivalent.
E01 must document the tested platform-specific setup and PDF utility installation.

## Planned commands

The `fixtures` command is available and publishes a labeled synthetic review.
It does not read evaluation requests, call OpenRouter, or write `output.csv`.
The other commands below remain later units.

Use the virtual environment's Python from the repository root:

    python3 code/main.py preflight
    python3 code/main.py preflight --online
    python3 code/main.py fixtures --run-dir runs/fixtures
    python3 code/main.py probe --budget-usd 0.25
    python3 code/evaluation/main.py --suite all --run-dir runs/evaluation --budget-usd 0.75
    python3 code/main.py run --run-dir runs/final --budget-usd 4
    python3 code/main.py validate --input output.csv --run-dir runs/final
    python3 code/package.py --output code.zip --run-dir runs/final

No-argument code/main.py will default to the full evaluation-request audit.
Resume and offline replay require compatible validated checkpoints/caches.
An unfinished run must not replace a valid prior submission.

## Runtime models and budget

OpenRouter is the runtime gateway. **$5 is the cumulative project ceiling** across
probes, model selection, evaluation, retries and the final run, including work
initiated from either coding tool. Actual funded balance remains to be checked.

Use a small project-specific pilot to compare suitable semantic models such as
GPT-6.1 Sol and Claude Sonnet 5.5. Gemini 3.8 Flash is the proposed visual extraction
path. These are candidates, not measured winners. Record exact returned model
IDs/providers, tokens and costs. Prefer correctness; avoid broad comparisons or
running multiple full assessments without a concrete reason.

Initial allocations: $0.25 probes, $0.75 evaluation/model selection/refinement,
$4 final processing/retries. Unused allocation may be reassigned within $5 while
preserving completion feasibility. Do not purchase credits automatically.

## Participant data

Only participant-facing files under dataset/ may inform predictions.

| File | Role |
| --- | --- |
| deletion_requests.csv | 518 evaluation requests requiring answers |
| sample_deletion_requests.csv | 32 public sample requests |
| sample_output.csv | Reference answers for evaluation only |
| user_identities.csv | Current identity snapshots |
| user_audit_log.csv | Historical identity changes |
| system_activity.csv | Global operational activity and claims |
| deletion_rules.csv | Required treatment and retention policy |
| evidence_files.csv | Manifest for 94 evidence artifacts |
| dataset/output.csv | Blank format template, not the final output |

Evidence formats: logs, JSON, text, PNG, SQL and PDF. Inspect content, identity
links and time; manifest filenames alone do not establish case membership.
Compare relevant primary and replica tables. Workflow success is a claim rather
than proof of compliance. Never use organizer-only truth or case-family shortcuts.

## Required output

Write the final output.csv at the repository root:

    case_id,deletion_status,steps_json

It must contain exactly 518 data rows, one per expected case, sorted by case_id.
Allowed statuses are COMPLETE, INCOMPLETE and NOT_APPLICABLE. Non-deletion requests
require an empty JSON array.

Each step contains exactly step_no, phase, system_id, resource_id, operation,
state and evidence_id. Use only the allowed phase/operation/state combinations.
Number consecutively from 1. Sort by required phase and operation ordering,
then system_id and resource_id.

Findings and COMPLETE verification cite timely supporting file_id, activity_id
or audit_id values. INCOMPLETE remediation/future verification use empty
evidence IDs. Reconcile ordering with required flow/restore prerequisites;
investigate unsupported or conflicting plans before publication.

Preserve policy-required records and permitted stable tombstone references.
The full contract remains in problem_statement.md and AGENTS.md.

## Evaluation and usage reports

The following files are currently **unfilled report templates**:

- [Evaluation report](code/evaluation/evaluation_report.md)
- [Usage report](code/evaluation/usage_report.md)

E05 must report measured public/custom status, step, field, sequence and full-row
accuracy, at least three fictional custom cases, failures and improvements.
E06 must report actual final-run providers/models, calls, input/output tokens,
totals/averages, costs, retries and cache/preparation attribution.

Targets are not measurements. Hidden-set accuracy remains unknown.
Do not put essential explanations only in raw data that the judge may ignore.

Canonical reports live under code/evaluation/. The planned packager also includes
byte-identical copies under archive-root evaluation/ to satisfy both documented
path conventions. Verify equality.

## Submission and traces

| Item | Delivery |
| --- | --- |
| output.csv | Final validated predictions |
| code.zip | Runnable source, prompts, pins, README, tests and reports |
| log.txt | Genuine shared development transcript |
| agent-trace.zip | Relevant sanitized Codex and Cursor session exports, separately prepared |
| AI interview | User explains actual architecture, evidence, results and limitations |

Package only the explicit allowlist. Exclude supplied dataset/, environments,
dependency caches, runs/, Git metadata, credentials, raw provider responses and
nested archives. Submit predictions and transcripts separately from code.zip.

Before submission verify all rows/steps/citations, report/run consistency, archive
integrity, identical report copies, clean setup and absence of prohibited content.
Do not submit template metrics or claim a test/model run that did not happen.

Submission page:
[https://www.hackerrank.com/contests/hackerrank-orchestrate-october26/challenges/ghost-data-still-exists](https://www.hackerrank.com/contests/hackerrank-orchestrate-october26/challenges/ghost-data-still-exists)

## Next action

Remain in documentation-only mode until the user starts Prompt 2. Then read the
approved handoff and current state, verify reality, and obtain E01 authorization
unless it was already explicitly supplied. Planning approval alone is not permission
to begin implementation.
