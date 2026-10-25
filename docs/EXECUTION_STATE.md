# EraseCase — Shared Execution and Tool Handoff Notes

Updated: 25 October 2026, 12:46 IST
Blueprint version: 1.3; approved section content remains v1.1
Canonical plan: [ENGINEERING_BLUEPRINT.md](ENGINEERING_BLUEPRINT.md)
Planning: Prompt 1 COMPLETE; all 14 sections APPROVED; CHECK: READY.
Execution: E03 VERIFIED_PENDING_COMMIT on main. E04 is not authorized.
Current harness: Codex Desktop.
Current verified runtime model: gpt-5.6-sol.
Current baseline: main / 1acb93b81d6bacb624bac6e636a54c69aa199d3b.
Verified remote state: origin/main / 1acb93b81d6bacb624bac6e636a54c69aa199d3b.
Remote policy: push verified step commits directly to origin/main; verify its SHA after every push.
Legacy branch: build/erasecase is retired by this consolidation after origin/main verification.
Implementation units: E01 COMMITTED; E02 COMMITTED; E03 VERIFIED_PENDING_COMMIT; E04–E07 NOT_STARTED.
Next action: commit and push the verified E03 outcome, then stop before E04.

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
are ready for the standalone commit and push.

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

## Latest action

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
- Codex owns core implementation, testing, debugging and final correctness.
- Cursor owns CLI/report presentation and documentation; no web frontend.
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
| E03 | VERIFIED_PENDING_COMMIT | Codex | KEEP CODEX for E04 |
| E04 | NOT_STARTED | Codex | KEEP CODEX for E05 |
| E05 | NOT_STARTED | Codex | KEEP CODEX for E06 |
| E06 | NOT_STARTED | Codex | SWITCH TO CURSOR for E07 documentation |
| E07 | NOT_STARTED | Cursor then Codex | SWITCH TO CODEX for final checks before the E07 commit |

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

Not completed: public or custom-case execution, full-dataset audit, packaging,
or submission. No generated root output.csv or code.zip exists. Report templates
contain no measured evaluation results.

## Resume boundary

E03 is verified and awaiting its standalone commit and push. After local HEAD
and origin/main match the new commit, stop at the A1 boundary. KEEP CODEX is the
recommended owner for E04, but E04 must not begin without explicit authorization.


## Baseline preservation and current E01 delta

- The canonical engineering blueprint still has all 14 approved sections and a consistent manifest.
- Historical planning/documentation changes remain present and unstaged.
- Main contains the verified E01 application/configuration/test commit d854687.
- Future work remains on main and is pushed directly to origin/main after verification.
- A local ignored .venv exists; no root .env, output.csv or code.zip exists.
- No prediction, packaging action or submission has occurred.
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
