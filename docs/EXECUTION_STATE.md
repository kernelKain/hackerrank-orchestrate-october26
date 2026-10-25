# EraseCase — Shared Execution and Tool Handoff Notes

Updated: 25 October 2026, 15:25 IST
Blueprint version: 1.4; approved section content remains v1.1
Canonical plan: [ENGINEERING_BLUEPRINT.md](ENGINEERING_BLUEPRINT.md)
Planning: Prompt 1 COMPLETE; all 14 sections APPROVED; CHECK: READY.
Execution: E07 COMPLETE on main. Screenshot linking is implemented and the 518-row output was regenerated. The user submits.
Current harness: Cursor.
Current verified runtime model: Grok 4.7.
Verified implementation baseline: E07 / 08cd9b9d4137c3b9776075ec3f76f345e39e22b8, plus the screenshot-linking diff.
Verified implementation remote: origin/main contains E07 / 08cd9b9d4137c3b9776075ec3f76f345e39e22b8.
Remote policy: push verified step commits directly to origin/main; verify its SHA after every push.
Legacy branch: build/erasecase is retired by this consolidation after origin/main verification.
Implementation units: E01 COMMITTED; E02 COMMITTED; E03 COMMITTED; E04 COMMITTED; E05 COMMITTED; E06 COMMITTED; E07 COMMITTED.
Next action: the user submits output.csv, code.zip, log.txt, and agent-trace.zip. Do not claim the upload.

## A15 ownership amendment — 25 October 2026, 12:51 IST

The user reported that Codex usage is exhausted for now and directed that the
remaining work be completed with Cursor. Cursor therefore owns E04–E07,
including core implementation, model integration, evaluation, debugging,
accounting, documentation and final technical verification. Existing product,
correctness, security, budget, A1 authorization and per-verified-step commit
contracts remain unchanged. Cursor must verify and log its own exact runtime
model before acting. This handoff does not itself authorize E04.

## E04 verification — 25 October 2026, 13:31 IST

The user authorized E04. Cursor implemented deterministic deletion intent,
policy assessment, contradiction notes, ordered planning, strict step
validation, and the unused strict intent-request builder. Models do not choose
operations, order, or serialization. Activity rows stay claims. A resource
enters a plan only from participant evidence linked by a supported identifier,
or by a trace whose strong identifiers all belong to that subject.

The initial public-sample evaluation scores 32/32 deletion statuses and 9/32
exact step sequences. Every finding cites evidence. Future remediation and
verification steps use an empty evidence id. The 23 sequence misses are
compliant records with no supported identifier, or records whose only file was
captured after `audit_at`. They are omitted rather than guessed. No reference
labels are read during assessment. `sample_output.csv` is read only by the
evaluation test. Root `output.csv` was not written.

Thirty-seven offline tests pass. No OpenRouter call was made. Measured project
spend remains the E01 total of $0.0014705, with a conservative ceiling remainder
of at least $4.9934735. Funded balance is still unverified. The reviewed E04
files were committed as `246db0f8658445a5df47bce3f1103853fd331d1e` with subject
`feat(audit): reconcile policy and build deletion plans`. Local HEAD,
origin/main and the remote main ref were verified equal after the push. This
ledger update and the current log append are bookkeeping for the next commit
boundary.

## E03 verification — 25 October 2026

The user's `Execute this` instruction authorized the next eligible A1 outcome.
Codex implemented strict participant-data ingestion, time-aware current and
historical identity reconstruction, safe all-format evidence extraction,
cutoff-aware evidence/resource indexes, and transactional persistence. SQL is
executed only in restricted in-memory SQLite with filesystem, extension,
trigger, view and virtual-table operations blocked. Images are validated and
explicitly marked `VISION_REQUIRED` for E04 rather than treated as extracted facts.

All 518 request emails resolve to exactly one supported subject. The full
participant manifest produces 94 extraction outcomes, 8,125 observations,
4,011 activity links and 4,556 identity facts; all are persistable and 11 PNGs
are explicitly queued for vision. Representative screenshots and rendered PDF
pages were compared to extracted structure. Twenty-eight offline tests pass,
dependency checks and offline preflight pass, and no OpenRouter call or charge
was made. The reviewed E03 files plus prior expected handover/log bookkeeping
were committed as `acc586ce61029a6449a107ff0c79eaba4a45be51` with subject
`feat(evidence): index time-aware identities and records`. Local HEAD,
origin/main and the remote main ref were verified equal after the push.

## E02 verification — 25 October 2026

The user approved the fixture review. Cursor committed and pushed
`1acb93b81d6bacb624bac6e636a54c69aa199d3b` with subject
`feat(cli): add fixture review and diagnostics`. Local HEAD and origin/main
match that SHA. The commit contains the fixture adapter, presentation helpers,
CLI wiring, fixture tests, and the README command note. Eighteen offline tests
passed before the commit. Root `output.csv` was not created and OpenRouter was
not called. `runs/` stays ignored. This ledger and the append-only log remain
uncommitted bookkeeping. The next action is SWITCH TO CODEX for E03 after the
user authorizes that unit.

## Cursor resume — 25 October 2026, 12:19 IST

Cursor read AGENTS.md, the approved blueprint and this ledger, then reconciled Git.
`main` and `origin/main` both point to `44bc63b30e465c3949b188caac6333927a58dacc`.
The working tree was clean before this resume note. E01 remains the last verified
implementation unit. E02 is still NOT_STARTED. No fixture CLI, report, or test
files were changed. The next action is explicit A1 authorization of E02.

## E05 verification — 25 October 2026, 14:00 IST

The user authorized E05. Cursor extended local intent coverage for Portuguese
`exclusão`, Korean `삭제`, and three keep/correct phrases. All 518 request texts
now resolve without a model. Public status stayed 32/32. Exact sequences stayed
9/32, with 158 matched steps, 0 extra steps, and 35 omissions. Every omission
lacks a supported identifier, is absent from the cited file, or appears only
after `audit_at`. None is a linked record the planner dropped.

Eight fictional cases cover the required replica, export, and compliant-tombstone
scenarios plus exposed tombstone, reactivated flow, post-cutoff, unlinked
analytics, and a zero-row retained audit. Five independently specified cases
match exactly. A zero-row security audit is no longer verified as present.
The packager writes 39 allowlisted members, duplicates the two reports at
archive-root `evaluation/`, and excludes the run directory. An extracted archive
imports. Forty-nine offline tests pass. Preflight passes. No OpenRouter call
was made. The 518-request timing pass took 0.59 seconds to load and 35.64
seconds to assess. Root `output.csv` was not written.

## Cursor resume — 25 October 2026, 13:36 IST

Cursor reconciled blueprint v1.4 with Git. Local main, origin/main and HEAD match
`246db0f8658445a5df47bce3f1103853fd331d1e`. Uncommitted files are E04 bookkeeping
plus this resume: the blueprint execution-status lines, this ledger, and log.txt.
The footer next-action line still pointed at E02; it now points at E05. E05 was
not started. No OpenRouter call was made.

## Latest action

Completed and committed the authorized E04 unit. Commit
`246db0f8658445a5df47bce3f1103853fd331d1e` contains intent classification,
policy assessment, ordered plans, validators, the intent prompt, and the
trace-link evidence correction. Thirty-seven offline tests pass. The public
sample scores 32/32 statuses and 9/32 exact sequences. The commit is pushed to
origin/main and the local, tracking and remote refs match. No OpenRouter call,
root output.csv, packaging or submission occurred. E05 was not started.

Historical E01 record:

Completed and committed the authorized E01 unit. The standalone commit
d85468763d46a25b8ec59139d87aa6cc9ca77acd establishes root secret exclusions,
placeholder configuration, pinned runtime/test dependencies, strict versioned
contracts, CLI/preflight/OpenRouter boundaries, cost reservation, transactional
run-state storage, offline CI and initial tests.

The clean Python 3.14 environment installed successfully and 11 tests pass.
Offline preflight confirms the expected 518 requests, 32 samples, 94 evidence
files, Poppler tools and ignored secret paths. Online preflight authenticated,
and all three approved candidate IDs were available. The strict-schema semantic
probe returned DELETE through openai/gpt-6.1-sol/OpenAI for $0.000218; the
synthetic-image probe returned ERASECASE 42 through google/gemini-3.8-flash/
Google AI Studio for $0.0012525. A first schema attempt stopped before vision
and has a conservative uncertain reservation of at most $0.005056. Measured
successful cost is $0.0014705; conservative cumulative E01 exposure is at most
$0.0065265, leaving at least $4.9934735 of the project ceiling. E01 and the
approved planning/documentation changes are consolidated directly onto main in
a2de2cd21eed7f66eef3c561dccb464c52658ffd. Local HEAD, its upstream and the remote
main ref were verified equal. The required current-turn bookkeeping is committed
and pushed next; only then is the obsolete build/erasecase branch removed. No
submission occurred.

## Current decisions

- A1: user authorizes one outcome at a time.
- PER_VERIFIED_STEP: a standalone commit after each verified step.
- All implementation is committed and pushed directly to main; no new branches.
- Each authorized, verified step receives its own commit and push to origin/main.
- Codex completed E01 and E03; its usage is currently exhausted.
- Cursor owns all remaining E04–E07 implementation and final verification under A15; no web frontend.
- The cumulative OpenRouter ceiling is $5; actual funded balance is unverified.
- E01 establishes root .gitignore exclusions before local .env credential entry.
- Runtime models are selected through a bounded project-specific pilot.
- Build/submission target is 5 PM IST; interview is planned after 6 PM.
- Portal deadlines and interview scheduling are user-managed.
- Both tools share root log.txt and these notes; one harness edits at a time.

## Next implementation owner

| Unit | Status | Owner | Required recommendation |
| --- | --- | --- | --- |
| E01 | COMPLETE ON MAIN — d85468763d46a25b8ec59139d87aa6cc9ca77acd | Codex | SWITCH TO CURSOR for E02 |
| E02 | COMPLETE ON MAIN — 1acb93b81d6bacb624bac6e636a54c69aa199d3b | Cursor | SWITCH TO CODEX for E03 |
| E03 | COMPLETE ON MAIN — acc586ce61029a6449a107ff0c79eaba4a45be51 | Codex | SWITCH TO CURSOR for E04 under A15 |
| E04 | COMPLETE ON MAIN — 246db0f8658445a5df47bce3f1103853fd331d1e | Cursor | KEEP CURSOR for E05 |
| E05 | COMPLETE ON MAIN — 3341e47788077f1291427adefdede781f2152c58 | Cursor | KEEP CURSOR for E06 |
| E06 | COMPLETE ON MAIN — 0fb883ff3a46bee441bfd66cc944fbd230a3b4c5 | Cursor | KEEP CURSOR for E07 |
| E07 | COMPLETE ON MAIN — 08cd9b9d4137c3b9776075ec3f76f345e39e22b8 | Cursor | User submits |

## Handover template

- Time and current/target harness:
- Actual current runtime model, verified rather than inferred:
- Handoff version and authorized unit:
- Branch and actual HEAD:
- Completed unit and actual commit ID:
- Changed/uncommitted files and ownership:
- Checks run, results and evidence paths:
- Acceptance criteria verified or unresolved:
- Remaining failures/blockers:
- Run IDs, cumulative charges, pending reservations and remaining allowance:
- Next permitted action:
- Required stop/gate:
- Recommendation: KEEP CODEX / SWITCH TO CURSOR / SWITCH TO CODEX, with reason.

The receiving harness reads AGENTS.md, ENGINEERING_BLUEPRINT.md and these notes, reconciles
actual state, and appends its own SESSION START to root log.txt. Do not fabricate
entries for another harness. E07's mid-step handover lists its uncommitted docs.

## Verification state

Completed during E01: protected secret paths, clean dependency installation,
Python syntax checks, 11 offline unit tests, dependency consistency, local and
online preflight, CLI help, bounded cost reservation, semantic strict-schema
proof, synthetic-image vision proof, complete staged-diff review and standalone
commit verification. The workflow consolidation commits the approved documentation
and shared log on main before the obsolete branch is removed.

Completed during E02: fixture CLI, three synthetic verdicts, failure and
recovery scenarios, 18 passing offline tests, UX approval, and the pushed
commit 1acb93b81d6bacb624bac6e636a54c69aa199d3b.

Verified during E03: strict CSV contracts; complete historical identity chains;
one supported identity per evaluation request; safe JSON, text/log, SQL, PDF and
PNG intake; replica preservation; availability/event-time filtering; strong-ID
indexing without name-only joins; activity claims and links; durable index state;
and representative original-artifact comparison. Twenty-eight tests pass.

Verified during E04: deletion versus non-deletion intent, including an
unresolved stop for ambiguous text; policy actions for delete, redact,
anonymize, retain, tombstone and active flow; contradiction notes; ordered
steps with cited findings and empty future evidence ids. The initial public
evaluation is 32/32 status and 9/32 sequence. Thirty-seven tests pass.

Not completed: the 23 public sequence omissions remain, because they are not
supported by a timely identifier. E06 wrote the gitignored 518-row root
`output.csv` and the measured usage totals. Submission packaging and the E07
inspection remain.

## Cursor resume — 25 October 2026, 14:02 IST

Cursor reconciled blueprint v1.4 with Git. Local main, origin/main, and HEAD match
`3341e47788077f1291427adefdede781f2152c58`. Uncommitted files are E05 post-commit
bookkeeping: this ledger and log.txt. E06 was not started. The official challenge
end time is not configured. The user-managed feature freeze is 3 PM IST and the
build target is 5 PM IST. No OpenRouter call was made.

## E06 verification — 25 October 2026, 14:15 IST

The user authorized E06. Cursor ran the frozen local auditor for all 518
requests, validated the candidate, and published root `output.csv`. Status
counts are COMPLETE 177, INCOMPLETE 335, and NOT_APPLICABLE 6. Output SHA-256
is `6d28e09ea4308f2acaf4598b0c48554e858fb9ea5edd0b6d601e8d4c51f54c10`. The
evidence fingerprint is `4a3d1956cbeac82dc72a3e67cabe599970ac5d37db961053134c252dbfa1c82f`.
Validation re-hashed all 94 evidence files and matched both fingerprints.
The run made 0 model calls and added $0. Eleven PNGs remain `VISION_REQUIRED`.
Public re-score stayed 32/32 statuses and 9/32 exact sequences. Fifty-three
offline tests passed. Preflight passed. The reviewed files were committed as
`0fb883ff3a46bee441bfd66cc944fbd230a3b4c5` with subject
`docs: record final audit results and usage`. Local HEAD, origin/main, and the
remote main ref were verified equal after the push. Root `output.csv` and
`runs/` stay ignored. E07 was not started.

## Resume boundary

E06 is complete on main. Local HEAD, origin/main, and the remote main ref all
match `0fb883ff3a46bee441bfd66cc944fbd230a3b4c5`. Stop at the A1 boundary.
KEEP CURSOR for E07. Do not start E07 until the user authorizes that unit.

## Cursor resume — 25 October 2026, 14:18 IST

Cursor reconciled blueprint v1.4 with Git. Local main, origin/main, and HEAD match
`0fb883ff3a46bee441bfd66cc944fbd230a3b4c5`. Uncommitted files are post-E06
bookkeeping: this ledger and log.txt. Root `output.csv` exists, has 519 lines,
and is gitignored. E07 was not started. The official challenge end time is not
configured. The user-managed feature freeze is 3 PM IST and the build target is
5 PM IST. No OpenRouter call was made. A15 assigns E07 final inspection to
Cursor; the older Codex review sentence in the E07 queue row does not restore a
Codex gate while Codex usage is exhausted.

## E07 verification — 25 October 2026, 14:40 IST

The user authorized E07. Cursor polished the README and trace instructions to
the measured E01–E06 facts, added `.gitignore` to the package allowlist, and
ignored `agent-trace/` and `agent-trace.zip`. Fixture review now proves it does
not change an existing root `output.csv`. The archive test rejects a provider-key
prefix and a private-key banner without embedding those strings in source.

Fifty-three offline tests passed. Offline preflight passed. `validate` matched
output SHA-256 `6d28e09ea4308f2acaf4598b0c48554e858fb9ea5edd0b6d601e8d4c51f54c10`
and evidence fingerprint `4a3d1956cbeac82dc72a3e67cabe599970ac5d37db961053134c252dbfa1c82f`.
`code.zip` has 42 members. The two report copies are byte-identical. It contains
no dataset, run directory, nested archive, or `.env` member. `.env` is untracked.
A fresh extract with the participant dataset supplied by symlink installed from
the pinned requirements, passed preflight, and passed the same 53 tests. No
OpenRouter call was made.

`agent-trace.zip` is gitignored and separate. It contains two 25 October 2026
Codex rollouts that name this repository and the Cursor transcripts for this
checkout, plus a short export note. The staged copies had one long provider-key
token replaced. No local secret value, URL-encoded form, Base64 form, or long
key token remains in the archive. Original harness files were not modified.
Portal submission was not performed. The reviewed files were committed as
`08cd9b9d4137c3b9776075ec3f76f345e39e22b8` with subject
`build: prepare validated submission materials`. Local HEAD, origin/main, and
the remote main ref were verified equal after the push. This SHA line is
post-commit bookkeeping and is left uncommitted.


## Baseline preservation and current E01 delta

- The canonical engineering blueprint still has all 14 approved sections and a consistent manifest.
- Historical planning/documentation changes remain present and unstaged.
- Main contains the verified E01 application/configuration/test commit d854687.
- Future work remains on main and is pushed directly to origin/main after verification.
- The E01 snapshot had a local ignored .venv and no root .env, output.csv, or code.zip.
- E06 later wrote the gitignored root output.csv. Packaging and portal submission have still not occurred.
- The current two turn records also appear once near the start of log.txt because
  an append patch matched an older anchor; canonical copies are at the file end.
  The earlier copies were preserved rather than rewriting append-only history.

The consolidated planning/documentation set includes:
AGENTS.md, CLAUDE.md, README.md, problem_statement.md, agent_trace_instructions.md,
docs/PRODUCT_BLUEPRINT.md, docs/ENGINEERING_BLUEPRINT.md,
docs/EXECUTION_STATE.md, code/evaluation/evaluation_report.md and
code/evaluation/usage_report.md. Root log.txt remains append-only.
E01's verified-step commit and the approved documentation consolidation are kept
as distinct commits. Continue staging only reviewed files for each authorized unit.
