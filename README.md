# EraseCase

**Every deletion, accounted for.**

EraseCase is the deletion-audit agent for HackerRank Orchestrate October 2026:
**Ghost Data Still Exists**. It reconstructs evidence at each request's audit
cutoff and produces the required findings, remediation, and verification.

## Current status

**E01–E07 are complete on main.** The user still submits the portal files.
This repository does not record a portal upload.

The canonical plan is [docs/ENGINEERING_BLUEPRINT.md](docs/ENGINEERING_BLUEPRINT.md),
version 1.4. The frozen local run wrote root `output.csv` with 518 sorted rows:
COMPLETE 169, INCOMPLETE 343, and NOT_APPLICABLE 6. Output SHA-256
`5c75a2763b3a0ee6902b53fd2d5bc173e006a1504ff518bf54a2ef179c1bdce8`. Evidence
fingerprint `4a3d1956cbeac82dc72a3e67cabe599970ac5d37db961053134c252dbfa1c82f`.
Eleven PNG files were read by `google/gemini-3.8-flash`. Seven contained
identifiable records and four abstained. The model does not choose steps.

| Document | Purpose |
| --- | --- |
| [Approved engineering blueprint](docs/ENGINEERING_BLUEPRINT.md) | Complete specification, directive, step/tool map and readiness manifest |
| [Product blueprint](docs/PRODUCT_BLUEPRINT.md) | Approved product boundary and amendments |
| [Execution state](docs/EXECUTION_STATE.md) | Current unit, checks, commits, budget and tool handovers |
| [AGENTS.md](AGENTS.md) | Mandatory instructions and shared logging contract |
| [Problem statement](problem_statement.md) | Challenge input/output and policy contract |
| [Trace instructions](agent_trace_instructions.md) | Relevant session-export requirements |
| [Evaluation report](code/evaluation/evaluation_report.md) | Measured public and fictional results |
| [Usage report](code/evaluation/usage_report.md) | Measured probes, tokens, and costs |

## Approved build workflow

The user authorizes one outcome at a time under A1. Work is committed and pushed
directly to `main`, with a separate commit after each verified step. There are
no implementation or phase branches, and step outcomes are not grouped into one
commit.

| Step | Outcome | Tool |
| --- | --- | --- |
| E01 | Foundation, protected configuration, contracts and access proof | Codex |
| E02 | Fixture CLI/report journey and mandatory UX approval | Cursor |
| E03 | Evidence, historical identity and provenance | Codex |
| E04 | Audit state, policy, challenge checks and ordered resolution | Cursor |
| E05 | Evaluation, debugging, safety and release tooling | Cursor |
| E06 | Final 518-case run and reconciled reports | Cursor |
| E07 | Documentation polish and final technical inspection | Cursor |

Amendment A15 assigned E04–E07 to Cursor, including final inspection, after
Codex usage was exhausted. Both tools use the same checkout, root `log.txt`,
and execution notes. Only one edits at a time. No web frontend, dashboard,
deployment, video, or presentation is part of the approved scope.

Working target: build and submit by **25 October 2026, 5 PM IST**. The user
plans the interview after 6 PM and manages the actual portal and interview
deadlines. This working target is not a verified official cutoff. The official
challenge end time is not configured in this repository.

## Setup

Verified runtime: Python 3.14.4 in the local virtual environment. Preflight
accepts Python 3.12 or newer. Dependencies are `requests`, Pydantic, Pillow,
python-dotenv, and Pytest, pinned in `code/requirements.txt` and
`code/requirements-dev.txt`. SQLite comes with Python. Preflight also requires
`pdftotext` and `pdftoppm` on `PATH`.

From the repository root:

```text
python3 -m venv .venv
.venv/bin/python -m pip install -r code/requirements-dev.txt
.venv/bin/python code/main.py preflight
```

Windows uses the virtual environment's `Scripts\python.exe` equivalent.

Copy `.env.example` to `.env` only when an online probe is needed, and replace
the placeholder locally. The application loads the root `.env` without
overriding existing environment variables. Only `.env.example` may be
committed. `.env`, `output.csv`, `code.zip`, `agent-trace.zip`, and `runs/`
are ignored. Do not paste the OpenRouter key into chat, logs, or the archive.

## Commands

`fixtures` publishes a labeled synthetic review and does not write `output.csv`.
`evaluation.main` scores the public sample and fictional cases offline.
`package.py` writes the source archive. `run` publishes `output.csv` after
validation, and `validate` recomputes its fingerprints.

Use the virtual environment's Python from the repository root:

```text
.venv/bin/python code/main.py preflight
.venv/bin/python code/main.py preflight --online
.venv/bin/python code/main.py fixtures --run-dir runs/fixtures
.venv/bin/python code/main.py probe --budget-usd 0.25
PYTHONPATH=code .venv/bin/python -m evaluation.main --suite all --run-dir runs/evaluation --budget-usd 0
.venv/bin/python code/main.py run --run-dir runs/final --budget-usd 4
.venv/bin/python code/main.py validate --input output.csv --run-dir runs/final
.venv/bin/python code/package.py --output code.zip --run-dir runs/final
```

`probe` and `preflight --online` can spend or authenticate. The frozen final
run and the offline evaluation made no model calls. No-argument `code/main.py`
audits every evaluation request. Resume and offline replay require a compatible
validated checkpoint. An unfinished run does not replace a valid prior
`output.csv`.

## Runtime models and budget

OpenRouter is the runtime gateway. **$5 is the cumulative project ceiling**
across probes, model selection, evaluation, retries, and the final run.
Funded balance remains unverified.

E01 measured two successful probes: `openai/gpt-6.1-sol` through OpenAI for
$0.000218, and `google/gemini-3.8-flash` through Google AI Studio for
$0.0012525. Measured successful cost is $0.0014705. A first schema attempt
stopped before vision and remains an uncertain reservation of at most
$0.005056. Conservative exposure is at most $0.0065265, leaving at least
$4.9934735 of the ceiling. These figures are not treated as zero and are not
reset by later units.

No production model is selected. Intent, policy, order, and serialization stay
in code. The final 518-row run read 11 screenshots, used 32,484 tokens
including one discarded truncated call, and added $0.068787.
Candidate IDs remain `openai/gpt-6.1-sol`, `anthropic/claude-sonnet-5.5`, and
`google/gemini-3.8-flash`. Do not purchase credits automatically.

## Participant data

Only participant-facing files under `dataset/` may inform predictions.

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

Evidence formats: logs, JSON, text, PNG, SQL, and PDF. Inspect content,
identity links, and time. Manifest filenames alone do not establish case
membership. Compare relevant primary and replica tables. Workflow success is a
claim, not proof of compliance. Never use organizer-only truth or case-family
shortcuts.

## Required output

Write the final `output.csv` at the repository root:

```text
case_id,deletion_status,steps_json
```

It must contain exactly 518 data rows, one per expected case, sorted by
`case_id`. Allowed statuses are `COMPLETE`, `INCOMPLETE`, and
`NOT_APPLICABLE`. Non-deletion requests require an empty JSON array.

Each step contains exactly `step_no`, `phase`, `system_id`, `resource_id`,
`operation`, `state`, and `evidence_id`. Use only the allowed
phase/operation/state combinations. Number consecutively from 1. Order phases
as `FINDING`, then `REMEDIATION`, then `VERIFICATION`.

Findings and `COMPLETE` verification cite timely supporting `file_id`,
`activity_id`, or `audit_id` values. `INCOMPLETE` remediation and future
verification use empty evidence IDs. Disable data flows and block unsafe
restores before changing dependent records.

Preserve policy-required records and permitted stable tombstone references.
The full contract remains in `problem_statement.md` and `AGENTS.md`.

## Measured results

Public samples: 32/32 deletion statuses and 9/32 exact sequences. Every emitted
public step matches a reference step. The 35 omitted steps have no supported
identifier, are absent from the cited file, or appear only after `audit_at`.
None is a linked record the planner dropped.

Five independently specified fictional cases match exactly, including the
replica, export, and compliant-tombstone scenarios. Hidden-set accuracy is
unknown. The full tables, empty-array convention, and case notes are in
[code/evaluation/evaluation_report.md](code/evaluation/evaluation_report.md).
Tokens and costs are in
[code/evaluation/usage_report.md](code/evaluation/usage_report.md).

### One grounded case

CUSTOM-03 is fictional and is not a participant row. At `audit_at` the
tombstone is redacted, the security audit is retained, analytics are
anonymized, the data flow is disabled, and the restore path is blocked. The
auditor returns `COMPLETE` with five evidence-backed verification steps and no
findings. The steps are listed in the evaluation report.

### One corrected failure

Twenty-nine of 518 requests previously raised `UnresolvedIntent`. They repeat
five phrases: Portuguese `exclusão`, Korean `삭제`, and three keep-or-correct
requests. The local lexicon now accepts the two deletion phrases and rejects
the three keep requests. All 518 texts resolve without a model, and the public
sequence score stayed 9/32.

A second correction: a linked security-audit lookup that returned zero rows was
eligible to be verified as present. It is now treated as absent and omitted.
The allowed operations still cannot say "restore this retained record."
CUSTOM-03E records that limitation.

## Evaluation and usage reports

Canonical reports live under `code/evaluation/`. The packager writes
byte-identical copies at archive-root `evaluation/`. Verify equality after
packaging.

Do not put essential explanations only in raw data that the judge may ignore.
Do not submit template metrics or claim a test or model run that did not happen.

## Submission and traces

| Item | Delivery |
| --- | --- |
| output.csv | Final validated predictions. Gitignored. 519 lines, including the header. |
| code.zip | Runnable source, prompts, pins, README, tests, and both report paths. Gitignored. |
| log.txt | Shared development transcript. Submit this file separately. |
| agent-trace.zip | Sanitized Codex and Cursor session exports. Gitignored and separate from code.zip. |
| AI interview | The user explains the actual architecture, evidence, results, and limitations. |

`agent-trace.zip` contains:

- `agent-trace/codex/`: the two 25 October 2026 Codex rollout JSONL files that name this repository
- `agent-trace/cursor/`: the JSONL transcripts, and the compaction files stored beside them, for this checkout

Older Codex rollouts are other work and are not included. Authentication
stores, `.env`, and provider configuration are not included. The trace copies
are scanned for local secret values, their URL-encoded and standard Base64
forms, and common key patterns. That scan does not catch every partial slice.
The active Cursor session is a point-in-time copy.

Package only the explicit allowlist. The archive excludes `dataset/`,
environments, dependency caches, `runs/`, Git metadata, credentials, raw
provider responses, and nested archives. Submit predictions and transcripts
separately from `code.zip`.

Submission page:
[https://www.hackerrank.com/contests/hackerrank-orchestrate-october26/challenges/ghost-data-still-exists](https://www.hackerrank.com/contests/hackerrank-orchestrate-october26/challenges/ghost-data-still-exists)

## Next action

Upload `output.csv` and the rebuilt `code.zip`. The code archive includes
`README.md` and `code/README.md`, with setup instructions and the audit
approach. `log.txt` is submitted separately. The 14:31 `agent-trace.zip` was
removed because it predates the screenshot-linking session; rebuild it before
that separate upload. Interview notes can use CUSTOM-03 and the intent-lexicon
correction above. Do not describe the 9/32 public sequence score as a hidden-set
result.
