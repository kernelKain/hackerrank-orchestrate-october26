# EraseCase — Approved Engineering Blueprint

Version: 1.4
Approval: Sections 1–14 approved on 25 October 2026.
Planning stage: Prompt 1 COMPLETE.
Planning readiness: READY.
Execution status: E01–E05 COMPLETE; E06–E07 NOT_STARTED; E06 awaits A1 authorization.

This is the canonical engineering blueprint. It consolidates the approved planning
sections and user amendments. Planning is complete and E01 has established and
verified the runtime foundation, model access boundary and initial costs. Do not
begin the next implementation unit until the user authorizes that A1 outcome.

Authority: platform/repository instructions, latest explicit user instructions,
approved amendments, approved handoff content, approved product packet, verified
repository reality, and applicable official challenge/technical sources.

## Applied amendment ledger

| ID | User-directed amendment | Applied effect |
| --- | --- | --- |
| A07 | Maximum $5 OpenRouter usage; project-local .env; Git exclusion | E01 establishes dotenv loading and secret exclusions before local credentials are populated. All paid work shares a $5 ceiling. |
| A08 | Codex and Cursor share the build | Codex owns core implementation, testing, debugging, model integration, correctness and final verification. Cursor handles CLI/report presentation and documentation. |
| A09 | Build sequentially by step; commit each step separately | Seven A1 units and one standalone commit after each verified unit. No phase branches or grouped step commits. Superseded by A14 only for branch/push handling. |
| A10 | Build/submit by 5 PM; interview after 6 PM | Interview leaves the build budget. The user manages portal/interview deadlines; the reported extra interview window is user-supplied, not independently verified. |
| A11 | Select the best suitable OpenRouter model within $5 | Run a small project-specific comparison; favor correctness, then acceptable latency/cost. Do not assume a globally best model from generic rankings. |
| A12 | Frontend means CLI and reports | User selected CLI/report polish. No web interface or dashboard is added. |
| A13 | User consolidated the complete approved plan into ENGINEERING_BLUEPRINT.md and removed the separate handoff file | Update references and manifest location; preserve all 14 approved section bodies and execution hold. |
| A14 | Commit and push all work directly to main; delete build/erasecase and create no further branches | Continue the stepwise verified-commit policy on main, push each completed step to origin/main, and do not create implementation or handoff branches. |
| A15 | Codex usage is exhausted for now; complete the remaining work with Cursor | Cursor owns E04–E07, including core implementation, model integration, evaluation, debugging, accounting, documentation and final technical verification. Existing contracts, A1 gates, spending limit and per-step commit policy remain unchanged. Cursor must verify and log its own runtime identity. |

## 1. Document Control and Sources

Project: EraseCase — Every deletion, accounted for.
Owner: Kshitij; solo builder using Codex and Cursor.
Repository: https://github.com/kernelKain/hackerrank-orchestrate-october26
Working checkout: resolve from the root AGENTS.md; do not hardcode paths in code.
Observed starting branch/HEAD: main / 0eddbbd; E01 was later completed as d854687.
Observed changes before this update: untracked docs/ and log.txt.
Required transcript: append-only root log.txt, shared by both harnesses.

Working target: build, verify, package and submit by 25 October 2026, 5 PM IST.
Feature freeze target: 3 PM IST; essential fixes afterward require revalidation.
Interview: user plans to complete it after 6 PM IST, outside the build schedule.
The user manages the exact portal cutoff and interview allowance. Do not invent
an official deadline or repeat deadline-intake questions.

Sources: AGENTS.md, problem_statement.md, README.md,
agent_trace_instructions.md, docs/PRODUCT_BLUEPRINT.md, participant-facing
dataset files, the attached Prompt 1 instructions and the latest user amendment.
No organizer-only information may inform predictions.

Planning is complete. E01 created the protected local configuration, dependencies,
application foundation, contracts, storage, tests and CI, and verified bounded
model access. The required Markdown report files remain templates without final
evaluation measurements. E02 is not authorized yet.

## 2. Locked Product Contract

EraseCase serves a privacy engineer reviewing the supplied fictional commerce
platform. A workflow success message can coexist with surviving personal data,
historical identifiers, secondary copies or processes that recreate data.

Promise: every conclusion has evidence, every violation has an action, and every
action has a verification.

Mechanism: establish deletion intent; resolve supported current/historical
identity; reconstruct relevant state at audit_at; apply the supplied policy;
challenge contradictions and omitted obligations; produce the prescribed result.

COMPLETE requires every relevant obligation satisfied, required retained records
available, and prohibited recreation/restore paths inactive. Include only
evidence-backed verification.
INCOMPLETE requires supported findings, a complete safe remediation plan and
future checks. Future remediation/verification evidence IDs are empty.
NOT_APPLICABLE requires a non-deletion request and steps_json=[].

Final output: exactly 518 rows, one per evaluation case, sorted by case_id, with
the exact columns case_id,deletion_status,steps_json.

Keep the competition-only boundary. No website, dashboard, model training,
commercial expansion, external prediction dataset, real-system deletion,
presentation or video. A separate demo is not required. Rankings and hidden-set
accuracy remain unknown.

## 3. Scope and Acceptance

MUST: full request and evidence-format coverage, grounded identity/time/policy
assessment, recreation risks, correct retention/tombstones, complete steps,
bounded model use, evaluation, reproducibility and required submission materials.
SHOULD: selective second-model review, extra adversarial cases and useful
investigation summaries. Cut these before mandatory coverage or verification.

| ID | Acceptance criterion | Main execution units |
| --- | --- | --- |
| AC-01 | Exact expected case coverage, unique/sorted rows and required header | E04, E06 |
| AC-02 | Exact step fields, allowed combinations, numbering and ordering | E01, E04, E06 |
| AC-03 | Correct deletion intent, including multilingual/keep-data requests | E04, E05 |
| AC-04 | Supported current/historical identity links without decoy absorption | E03, E05 |
| AC-05 | Cutoff-safe decisions and corroboration of operational claims | E03–E05 |
| AC-06 | Extraction outcome for every manifest item; no silent relevant gap | E01, E03–E06 |
| AC-07 | Correct deletion/redaction/anonymization/retention/tombstone treatment | E04, E05 |
| AC-08 | Recreation findings, safe dependencies and complete verification | E04, E05 |
| AC-09 | Existing, timely supporting citations; empty future evidence IDs | E03–E06 |
| AC-10 | Measured public/custom status, step, field and sequence results | E05, E06 |
| AC-11 | Reconciled providers/models, attempts, tokens, costs and cache work | E01, E04–E06 |
| AC-12 | Clean setup, understandable CLI, protected secrets and valid package | E01, E02, E05, E07 |

Targets: 32/32 public statuses and exact expected public step sequences.
Report actual results and unresolved misses honestly. Public-sample performance
is development evidence, not an unbiased hidden-set estimate.

Completion requires resolved essential extraction/correctness gaps and passing
structural, temporal, provenance and safety checks; a parseable CSV is insufficient.

## 4. UX and Frontend Contract

The user confirmed that Cursor's frontend work means CLI/report presentation.
Use ordinary readable text, selectable paths, Markdown reports and clear progress.
Do not introduce a web UI, branding project, mouse-only interaction or TUI framework.

Surfaces: command help, actionable preflight feedback, progress, run summary,
strict CSV, evaluation report, usage report and setup documentation.
Distinguish a valid INCOMPLETE verdict from an unfinished or failed execution.
Handle empty/missing inputs, slow work, partial runs, malformed data/responses,
network/quota/budget failures, interruption, recovery and success.

Fixture/live adapters share validated contracts. Fixture output is clearly labeled,
isolated from prediction destinations and never substituted for evaluation output.

E02 ends at the mandatory UX APPROVAL GATE. Show the local command, all three
verdict presentations, report examples, failure/recovery behavior and keyboard
interruption. The user approves this before substantial audit implementation.
No authority level bypasses the gate.

## 5. Architecture, Stack and Repository

Use one local Python pipeline:
ingest -> extract with provenance -> index identity/resources ->
establish intent -> cutoff-safe retrieval -> policy/state assessment ->
counterevidence checks -> deterministic planning/validation -> CSV/reports.

Models propose interpretations; code controls data boundaries, references,
policy checks, step construction, serialization and publication. Models receive
no shell or real-system deletion authority.

CSV/JSON use explicit parsers; logs/text preserve lines and trace/resource links.
Import SQL into isolated in-memory SQLite with restricted statements, disabled
extensions, filesystem restrictions and execution limits; inspect replica tables.
Use Poppler layout-preserving PDF text extraction and rendered-page vision where
needed. Use vision for PNG facts and relationships. Preserve originals.

Index supported identifiers and resource/process links without filename, resource
prefix or case-family shortcuts. Missing matches do not prove absence.
Filter observations by availability/capture and event time before case assessment.
Do not use later identity snapshots as evidence of earlier state.

Planned stack:

| Component | Selection |
| --- | --- |
| Runtime | Python 3.12–3.14; observed interpreter 3.14.4 |
| Core | argparse, csv, json, pathlib, datetime, hashlib, sqlite3, bounded concurrency |
| HTTP | requests==2.32.5 |
| Schemas | pydantic==2.14.1 |
| Images | Pillow==12.1.1 |
| Local configuration | python-dotenv==1.2.4; verify clean installation in E01 |
| PDF | external pdftotext/pdftoppm, observed locally; document setup |
| Tests | pytest==9.1.1 and offline CI |
| Persistence | local SQLite/checkpoints/content-addressed caches under runs/ |

Installed-package inspection and published capability are not clean-run proof.
No hosted server, database, authentication system or vector service is required.

Planned files:
code/main.py; code/erasecase/{contracts,ingest,evidence,identity,audit,planner,
models,storage}.py; code/prompts/; code/tests/; code/evaluation/;
code/requirements*.txt; code/pytest.ini; code/package.py; README.md;
.github/workflows/; .gitignore; .env.example.
The user's root .env remains local and excluded.

OpenRouter model selection is now a bounded project-specific pilot:

| Role | Candidate/default | Decision rule |
| --- | --- | --- |
| Semantic intent/ambiguous assessment | openai/gpt-6.1-sol versus anthropic/claude-sonnet-5.5 | Same small representative inputs; compare intent, obligations, citations, schema validity, latency and measured cost. |
| Visual extraction | google/gemini-3.8-flash | Check original images/pages against extracted facts; escalate only if essential facts remain unresolved. |
| Final runtime choice | Exact supported ID chosen from the pilot | Correctness first; prefer the less costly/faster option when quality is equivalent. |

Do not benchmark many models or run both semantic candidates on every case.
Use explicit IDs, validate endpoint parameters, record returned models/providers,
and reassess a candidate only for a concrete measured shortcoming.
No project-specific winner or actual account access is established yet.

## 6. Contracts, Data and Integrations

Resolve repository paths from the entry point. Load exactly the root .env using
python-dotenv with override=False, then read OPENROUTER_API_KEY from the environment.
An explicitly set environment value has precedence.

E01 must create .gitignore before populating local credentials. Exclude .env and
secret variants; allow only a placeholder-only .env.example. Verify ignored and
untracked status. Packaging independently excludes all actual secret files.
Never ask for the key in chat or expose it in command arguments/output.

Commands planned for Prompt 2:

    python3 code/main.py
    python3 code/main.py preflight
    python3 code/main.py preflight --online
    python3 code/main.py fixtures --run-dir runs/fixtures
    python3 code/main.py probe --budget-usd 0.25
    python3 code/main.py run --run-dir runs/final --budget-usd 4
    python3 code/main.py run --resume RUN_ID
    python3 code/main.py validate --input output.csv --run-dir RUN_DIR
    python3 code/evaluation/main.py --suite all --run-dir runs/evaluation --budget-usd 0.75
    python3 code/package.py --output code.zip --run-dir runs/final

No arguments defaults to the full evaluation-request run. Support explicit dataset,
output and run-directory overrides. Offline replay requires compatible complete
caches and cannot silently make model calls.
Exit codes: 0 success; 1 unexpected software failure; 2 usage/configuration;
3 validation failure; 4 unresolved evidence/provider/budget; 130 interruption.

Strict versioned contracts: DeletionRequest, IdentifierFact, Observation,
ResourceLink, PolicyObligation, CaseAssessment, ModelCallRecord and OutputStep.
Record original/normalized identifiers, supported validity intervals, source
locations, capture/event/availability times, observations, links, obligations,
contradictions, call attempts and accounting.
Unknown intent/evidence is an internal unresolved state, never a fourth CSV status.

OutputStep has exactly step_no, phase, system_id, resource_id, operation, state,
evidence_id. Construct locally and serialize by prescribed phase, operation,
system_id and resource_id ordering. Check dependency safety after disabling flows
and blocking restores; investigate residual conflicts instead of inventing fields
or silently changing canonical order.

Gateway: HTTPS POST https://openrouter.ai/api/v1/chat/completions with bearer auth,
explicit model, strict JSON schema and supported parameter routing.
Send local images as base64 image content with source-specific instructions.
Reject malformed/truncated/refused results and invented observation references.
No external search or unrelated integration is required.

Only evaluation code reads reference labels. Keep fixture, public, custom and
prediction namespaces isolated.
Record request IDs, stages, affected cases/files, attempts, returned model/provider,
tokens, reasoning/cache details where supplied, actual cost, latency and outcome.
Do not double-count reasoning tokens or treat missing charges as zero.

## 7. Security, Privacy and Reliability

Treat evidence instructions as untrusted data. Validate manifest paths inside the
participant directory, source fingerprints, schemas, references, temporal bounds,
image decoding and SQL/PDF resource limits.
Only relevant fictional evidence goes to the approved gateway.
Routine logs use IDs/error categories rather than identifiers or whole prompts.
Keep local credentials, caches, source evidence and raw provider responses outside
the archive. Shared workflow notes contain no secrets.

Defaults: at most 2 concurrent requests; connect timeout 10 s; read timeout 60 s;
logical deadline 180 s; 3 total attempts including fallback/repair; at most one
schema repair; intent batches at most 16; completion caps 4,096 for intent and
8,192 for extraction/semantic tasks. Verify endpoint compatibility and pilot quality.

Retry transient network/server/rate-limit failures within limits; do not loop on
authentication, funding or invalid configuration. Do not silently drop evidence to
fit a request: split with provenance or leave work unresolved.
Concrete contradictions drive targeted review; avoid generic repeated reconsideration.

All paid work, across models, retries, runs and coding harnesses, shares a maximum
$5 project allowance. Start with $0.25 access/extraction probes, $0.75 project
evaluation/model selection/refinement and $4 final processing/retries.
Unused portions may be reassigned within $5 while preserving final-run feasibility.
Stop if verified available funding is lower. Never purchase credits automatically.

Reserve conservative request/in-flight costs, reconcile actual charges, and keep
uncertain timed-out charges pending reconciliation. A retry may incur another
charge; do not claim remote idempotency without evidence.
Single-writer transactional run state preserves attempts, validated results and
usage. Cache keys include content, prompt/schema/model configuration and relevant
code fingerprints; case keys also include request, policy, cutoff and evidence.

Interruption stops dispatch, records uncertain requests and preserves checkpoints.
Validate a candidate CSV before atomically replacing root output.csv. Keep the
previous valid submission on failure; bind reports to run/output fingerprints.
Multiple artifact replacements are not a single atomic transaction.

Run only one coding harness at a time in this checkout. Handover includes the
branch, committed/uncommitted files, exact tool/model context, checks, blockers,
budget, active unit and next allowed action.

## 8. Testing and Deployment

Prompt 2 owns execution; no tests/installations/probes have run in Prompt 1.
Use offline contracts, core regressions, all-format extraction tests, model-adapter
tests, reliability fault injection and bounded live public/custom evaluation.
CI has no API credentials or paid inference. Mock tests are labeled accordingly.

Required custom cases:
CUSTOM-01: historical email, clean primary, surviving replica, later cleanup and a
same-name decoy -> INCOMPLETE with only supported timely findings.
CUSTOM-02: multilingual export request explicitly retaining the account ->
NOT_APPLICABLE with [].
CUSTOM-03: compliant tombstone, proper retention/redaction/anonymization, disabled
flow and blocked restore -> COMPLETE with supported verification only.
Add focused variants for exposed tombstone identifiers, removed retained data,
reactivated flows, timestamp changes and invalid citations.

Metrics: status accuracy; positional exact seven-field step accuracy using maximum
sequence lengths; multiset step precision/recall/F1 excluding step_no; positional
field accuracy penalizing missing/extra steps; exact ordered-sequence accuracy;
full-row accuracy requiring status plus sequence. Define empty-array conventions.
Report public and custom results separately, with case-level details and corrections.

Future setup and offline checks from the root:

    python3 -m venv .venv
    .venv/bin/python -m pip install -r code/requirements-dev.txt
    .venv/bin/python code/main.py preflight
    .venv/bin/python -m pytest -c code/pytest.ini code/tests -q
    .venv/bin/python code/main.py fixtures --run-dir runs/fixtures
    git check-ignore .env .env.local

Check that the secret file is not tracked, without printing its contents.
Windows uses the virtual environment's Scripts/python.exe equivalent.
Run the online/pilot/evaluation/final commands from Section 6 through that same
interpreter. Repeat paid work only when new changes/failures invalidate prior work.
Verify current final reports, output and budget, then package and inspect with:

    .venv/bin/python -m zipfile -t code.zip
    .venv/bin/python -m zipfile -l code.zip

All structural, temporal, provenance, safety and reliability regressions must pass.
Known essential defects block readiness. Accuracy targets do not become fabricated
results. Forecast full-run duration/cost from measured pilot work.
Check candidate-package setup in a fresh directory/environment with participant
data supplied separately. No hosting, browser/mobile checks or migrations are needed.
Version cache schemas; incompatible state goes to a new namespace without deleting
usage history. Retain valid previous artifacts for rollback.

## 9. Submission and Interview

By the working 5 PM target: validated root output.csv, inspected code.zip, genuine
root log.txt, relevant sanitized trace exports and upload-ready documentation.
The user manages actual portal submission/deadlines and confirms upload completion.
Interview preparation remains required; the interview itself occurs after 6 PM
according to the user's schedule. The reported extra 12-hour allowance is not
independently verified and must not be presented as an official fact.

Canonical reports: code/evaluation/evaluation_report.md and usage_report.md.
The packager includes byte-identical copies under archive-root evaluation/ to
satisfy both documented path conventions. Verify equality.
Include source, prompts, tests, pins, pytest configuration, evaluator, packager,
README and required readable reports. Include only placeholder configuration.
Exclude dataset/, environments, dependency caches, runs/, Git metadata, secrets,
raw provider responses, nested archives and actual local .env files.
Output/transcripts/trace archives remain separate from code.zip.

Preserve traces from BOTH Codex and Cursor, limited to relevant sessions, sanitized
and in original structured formats where available. If a harness has no raw
local export, use its documented interface-export fallback and disclose the gap.
Do not include authentication/configuration stores or unrelated history.

Documentation explains actual setup, architecture, model selection, measured
evaluation, costs, limitations and recovery. Essential content must be readable
Markdown/source, not only raw data ignored by the judge.
Prepare a brief explanation of one grounded case and an actual corrected failure.
No presentation, video or separate demo application is added.

Submission:
https://www.hackerrank.com/contests/hackerrank-orchestrate-october26/challenges/ghost-data-still-exists

## 10. Risks, Assumptions and Decisions

Main risks: access/funding, visual fact loss, false identity links, time leakage,
wrong retention/tombstone treatment, uncovered recreation paths, ordering conflicts,
unsupported model claims, cost/latency overruns, artifact mismatch and tool-handoff
drift. Required mitigations and triggers appear in Sections 3 and 5–9.
Under A15, Cursor owns remaining technical correctness. The user owns local secret entry, UX approval,
unit approvals, portal actions and the later interview.

VERIFY-EARLY: usable credentials/funds, clean installation, endpoint/model
compatibility, reliable format interpretation, actual project model selection,
run-duration/cost forecast and both harnesses' logging/export routes.
The balance is unknown; the user's $5 instruction is a ceiling, not a verified
balance. There have been no EraseCase inference calls during planning.
Technical execution gates remain even though deadline administration is user-owned.

Decisions superseding old text:
- One stepwise sequence directly on main, with individual verified-step commits and pushes.
- A1 approval before each unit; no phase approvals or per-phase integration.
- Cursor owns all remaining E04–E07 work while Codex usage is unavailable.
- Root .env with explicit dotenv loading and Git/archive exclusion.
- Quality-first project-specific model selection within a cumulative $5 ceiling.
- Interview after 6 PM; build/submission target remains 5 PM.

Preserve product/acceptance scope and genuine logging across switches. If essential
coverage becomes unattainable, reopen feasibility instead of silently cutting it.

## 11. Stepwise Delivery Schedule

This section replaces the previous five-phase/per-phase-branch plan.
All implementation work proceeds directly on main. Push each successfully verified
step to origin/main, and do not create implementation, phase or handoff branches.

| Step | Outcome | Owner | Estimate including contingency | Recommendation after completion |
| --- | --- | --- | --- | --- |
| E01 | Foundation, secret exclusions, contracts and feasibility | Codex | 45 min | Switch to Cursor for E02 |
| E02 | Fixture CLI/report UX | Cursor | 25 min | Switch to Codex for E03 |
| E03 | Evidence and identity indexing | Codex | 75 min | Switch to Cursor for E04 under A15 |
| E04 | Assessment, policy, challenge and output planning | Cursor | 75 min | Stay in Cursor |
| E05 | Evaluation, debugging and release tooling | Cursor | 85 min | Stay in Cursor |
| E06 | Final run, correctness and accounting | Cursor | 70 min | Stay in Cursor |
| E07 | Documentation polish, final inspection and handover | Cursor | 20 min | Cursor completes final checks; then user submits |
| Total | Seven individually verified/committed outcomes | | 395 min | |

The total removes the earlier 30-minute interview reservation. It includes
contingency; it is not a measured completion guarantee. Recalculate at Prompt 2
startup and cut SHOULD work first. Do not add implementation or phase branches.
Presentation work must not displace core correctness. Any tool switch is a user
handover, not an automatic launch or a fabricated session.

## 12. Execution Queue and Separate Commits

Shared preconditions: read the complete approved handoff/current amendments, obey
AGENTS.md, verify actual state, obtain A1 authorization and stay on main.
Each outcome includes focused verification, a standalone commit and a switch note.

| Step | Files/actions | Acceptance/checks | Standalone commit |
| --- | --- | --- | --- |
| E01 | Requirements incl. dotenv; root .gitignore and placeholder example before local secret entry; schemas; CLI/model/storage shells; initial tests/CI/setup notes; bounded probes | AC-02/06/11/12; install/preflight/contracts; secret ignore/untracked checks; account/schema/vision proof within budget | build: establish reproducible audit tooling |
| E02 | Presentation-only CLI/report work, isolated fixture adapter, help/progress/errors, fixture tests | AC-02/12 and mandatory UX APPROVAL GATE; user reviews fixtures before core work | feat(cli): add fixture review and diagnostics |
| E03 | ingest/evidence/identity/storage; all-format extraction, SQL replicas, temporal links and provenance | AC-04/05/06/09; parser/identity regressions and original-artifact comparison | feat(evidence): index time-aware identities and records |
| E04 | audit/planner/models/prompts/validators; obligations, contradictions, complete treatment and serialization | AC-01–09; core tests and initial public evaluation; manifest outcomes; no reference labels in inference | feat(audit): reconcile policy and build deletion plans |
| E05 | Public/custom evaluation, failure-driven fixes, safety/accounting tests, packager, clean setup and forecasts | AC-01–12; passing essential regressions, actual reports, project-model comparison and release feasibility | test(audit): validate assessments and harden failures |
| E06 | Frozen full-dataset run, output.csv and final reports; reconcile calls/caches/cost | AC-01/02/06/09/10/11; full run and provenance validator, 518 rows and consistent fingerprints | docs: record final audit results and usage |
| E07 | Cursor polishes README/review material within proven facts; Codex performs final package/citation/secret/integrity checks and records delivery state | AC-10/11/12; exact archive contents, equal reports, clean setup proof, both tool traces prepared | build: prepare validated submission materials |

Cursor may not change audit semantics, model choices or metrics while polishing.
Codex reviews Cursor's changes before relying on them. E07 remains IN_PROGRESS
until Codex's final technical checks pass; commit E07 once after those checks.

There is no GROUP_WITH_NEXT commit batch. The user's per-step instruction supplies
standing authorization to commit the reviewed unit after verification. Do not ask
for redundant commit permission. A failed or partial unit is not committed as done.
Stage only reviewed unit files, never broad unreviewed changes or secrets.
Generated archives are not staged automatically. Subsequent defects receive
explicitly recorded corrective work; never rewrite history to conceal them.

## 13. Execution State and Change Policy — APPROVED v1.1

Authority: A1, one explicitly approved outcome at a time.
Commit mode: PER_VERIFIED_STEP, superseding ASK and grouped batches.
Approval of a unit covers its implementation, focused checks, notes and separate
commit after success. It does not authorize the next unit, purchases, pushing,
portal upload, deadline changes or real-system deletion.
Mandatory UX approval and essential correctness gates still apply.

Track NOT_STARTED, IN_PROGRESS, FAILED_VERIFICATION, BLOCKED,
VERIFIED_PENDING_COMMIT and COMMITTED. Do not advance to the next unit until the
current unit's checks, required gate and separate commit are verified.
If the harness cannot perform a Git operation, report the actual restriction,
provide the exact user-run command and verify its outcome before advancing.

At each unit boundary report:
step outcome; changed files; checks/results; AC coverage; actual commit ID; cost
and remaining allowance; next unit; KEEP CODEX / SWITCH TO CURSOR / SWITCH TO CODEX,
with a reason. Update root log.txt and docs/EXECUTION_STATE.md.

Only one harness edits at a time. Before switching, record actual branch/HEAD,
clean/dirty files, active unit, verified checks, pending work, budget and exact
next allowed action. During E07, explicitly identify the Cursor-to-Codex review
handover and its uncommitted documentation files.
Each harness writes its own session/tool/model entries with authoritative values.
Do not invent Cursor work or guess its active model.

Append-only log and workflow notes can change after a commit to record its hash
and handover. Record this expected bookkeeping dirt; do not create an extra
implementation commit merely for self-referential commit metadata.

On resume, reconcile actual Git/run state with notes before proceeding. Reuse
compatible results, preserve charges and investigate uncertain remote outcomes.
Never discard/stash unrelated work to obtain a clean branch.
Explicit latest instructions supersede older plans; record impact, increment the
handoff version and revalidate affected work. Preserve unaffected decisions.

Current state after E01: planning approved; E01 complete at d854687 with protected
local configuration, 11 passing tests and bounded semantic/vision probes. E02–E07
remain not started. Work continues directly on main after each applicable A1
authorization. Recheck actual state before any authorized execution.

## 14. Prompt 2 Directive — APPROVED v1.1

Section version: 1.1
Status: APPROVED
Depends on: Sections 1–13 and amendments A07–A12.

You are executing the approved EraseCase blueprint. Preserve its product contract,
acceptance criteria, architecture, spending ceiling, step order and user amendments.
Planning approval does not start execution. Begin only after the user invokes
Prompt 2, and never in the same response that declares handoff readiness.

Before mutations, read the entire approved blueprint, amendment ledger,
docs/PRODUCT_BLUEPRINT.md, docs/EXECUTION_STATE.md and applicable AGENTS.md
instructions. Verify actual Git/runtime state, outstanding work, logging identity,
dependencies and remaining build capacity. Use only participant-facing data for
predictions. Do not reconstruct missing approved sections from memory.

Execution authority is A1. Execute only the next explicitly authorized step,
starting with E01. If it was not already authorized, present its scope and ask
for that approval. Existing authorization covers its described implementation,
focused verification, notes and separate commit; do not ask again for these actions.

Work directly on main through E01–E07. Do not create implementation, phase or
handoff branches, and do not restore phase merges, grouped commits or
COMMIT_MODE=ASK.
Commit mode is PER_VERIFIED_STEP: one standalone commit and push to origin/main
after each successfully verified step and any mandatory gate. Stage only reviewed step files. Do not
commit a failing or partial step, create an empty commit, or stage secrets and
unrelated work. Confirm the actual commit ID before treating the step as done.
If Git access is blocked, report the actual failure and verify a user-run
alternative before advancing. Ongoing log/handover metadata may change after
the commit to record its ID; do not create another implementation commit solely
for self-referential bookkeeping.

Codex completed E01 and E03. Under A15, Cursor owns all remaining E04–E07 work,
including core audit/model work, tests, debugging, safety, accounting,
documentation and final correctness. Cursor must preserve established semantics,
metrics and model decisions. No web frontend is authorized.

After every completed step report its outcome, changed files, checks/results,
acceptance coverage, actual commit ID, charges/remaining allowance and next unit.
Give a clear KEEP CODEX, SWITCH TO CURSOR or SWITCH TO CODEX recommendation and
reason. Record the same state in root log.txt and docs/EXECUTION_STATE.md.
Only one harness edits the checkout at a time. Before handover record branch/HEAD,
owned dirty files, checks, blockers, budget and exact next permitted action.
E07's mid-step Cursor-to-Codex handover explicitly lists its uncommitted docs.
Each harness verifies and logs its own exact runtime model; never fabricate
another tool's work or guess its model identity.

During E01 establish root .gitignore exclusions before local credential entry.
Use a root .env loaded explicitly with override=False and read the key from
the environment. Only placeholder .env.example may be committed. Verify actual
secret files are ignored/untracked and excluded independently by packaging.
Never request or expose a credential in chat, command arguments, logs or reports.

Keep cumulative OpenRouter use at or below $5 across probes, model selection,
evaluation, retries, both coding harnesses and the final run, subject to actual
available funding. Choose suitable explicit model IDs through the bounded pilot
in Sections 5–7; do not benchmark many candidates or duplicate every assessment.
Record actual models/providers, attempts, tokens and costs. Do not treat missing
usage as zero or reset accounting on resume. No automatic credit purchase.

Stop at E02's mandatory UX APPROVAL GATE, A1 unit boundaries, unresolved essential
evidence/correctness gaps, budget limits and actions outside authorization.
Preserve the prior valid output on failure. Resume only compatible validated
work; reconcile uncertain remote charges and revalidate affected changes.
Do not silently reduce coverage, invent completion, add a fourth output status,
weaken tests or change supplied data/reference labels to hide failures.

Maintain the 5 PM IST build/submission target; the user manages portal deadlines.
Interview completion is scheduled by the user after 6 PM, outside build capacity.
Prepare accurate materials without claiming the reported interview extension
is independently verified.

Accept latest explicit user amendments, record their impact/version and invalidate
only dependent work. Preserve unrelated files and the append-only shared log.
User uploads and interview completion must be confirmed, never assumed.

Assumptions and defaults: E01–E05 are complete on main; E06–E07 remain NOT_STARTED; E06 begins
in Cursor only after A1 authorization. Account access and the E01 semantic/vision
model probes are verified; project-wide model quality remains unverified.
VERIFY-EARLY: reconcile actual startup state, local secret exclusions, funded
access, selected endpoints and feasible remaining capacity before dependent work.
Impact: all 14 sections are approved and the cross-section planning readiness
review is complete. Prompt 2 has started and E01 is complete. The applicable A1
authorization is required before each remaining unit.

## Sources and verification

- Repository AGENTS.md, README.md, problem_statement.md and trace instructions.
- https://openrouter.ai/openai/gpt-6.1-sol
- https://openrouter.ai/anthropic/claude-sonnet-5.5
- https://openrouter.ai/google/gemini-3.8-flash
- https://openrouter.ai/docs/guides/features/structured-outputs
- https://openrouter.ai/docs/guides/routing/provider-selection
- https://openrouter.ai/docs/cookbook/administration/usage-accounting
- https://bbc2.github.io/python-dotenv/
- https://pypi.org/project/python-dotenv/

Published capability/pricing was inspected on 25 October 2026. Actual account
access, project quality, charges, clean setup and timing require execution proof.

## Handoff Manifest

Project: EraseCase
Handoff version: 1.2
Artifact mode: approved repository engineering blueprint
Canonical document: docs/ENGINEERING_BLUEPRINT.md

| Section | Approval |
| --- | --- |
| 1. Document Control and Sources | APPROVED v1.1, reconciled |
| 2. Locked Product Contract | APPROVED v1.1, carried forward |
| 3. Scope and Acceptance | APPROVED v1.1, carried forward |
| 4. UX and Frontend Contract | APPROVED v1.1, reconciled |
| 5. Architecture, Stack and Repository | APPROVED v1.1, reconciled |
| 6. Contracts, Data and Integrations | APPROVED v1.1, reconciled |
| 7. Security, Privacy and Reliability | APPROVED v1.1, reconciled |
| 8. Testing and Deployment | APPROVED v1.1, reconciled |
| 9. Submission and Interview | APPROVED v1.1, reconciled |
| 10. Risks, Assumptions and Decisions | APPROVED v1.1, reconciled |
| 11. Stepwise Delivery Schedule | APPROVED v1.1, replaces phase plan |
| 12. Execution Queue and Separate Commits | APPROVED v1.1, reconciled |
| 13. Execution State and Change Policy | APPROVED v1.1 |
| 14. Prompt 2 Directive | APPROVED v1.1 |

The approved section content remains v1.1. Blueprint v1.2 recorded the user-directed
canonical-document consolidation (A13); v1.3 records the direct-to-main workflow
(A14) and verified E01 state. All 14 section approvals remain valid.
Stale sections: NONE.
Planning blockers: NONE.
VERIFY-EARLY: credentials/funding, installation, endpoint support, extraction
quality, runtime model selection, timing/cost forecast and session exports.
Next Prompt 2 action: read this blueprint and instructions, verify actual state,
then execute E06 only after its A1 authorization.
CHECK: READY — E01–E05 complete; E06 awaits authorization.
