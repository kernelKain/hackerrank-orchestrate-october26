# EraseCase

**Every deletion, accounted for.**

## Approved Idea Packet — Prompt 0 → Prompt 1

| Field | Value |
| --- | --- |
| Packet version | 1.3 |
| Approval date | 25 October 2026 |
| Discovery mode | DEEP |
| Status | Product and engineering handoff approved; E01 complete; E02–E07 not started |
| Scope | Competition submission only |
| Working delivery cutoff | **25 October 2026, 5:00 PM IST** — user-selected target |

This is the approved product packet, reconciled with the latest user amendments. The complete approved engineering specification is [ENGINEERING_BLUEPRINT.md](ENGINEERING_BLUEPRINT.md); current state and tool handovers are in [EXECUTION_STATE.md](EXECUTION_STATE.md). Prompt 1 and E01 are complete. E02 awaits A1 authorization. No measured full-audit accuracy or prepared submission is claimed.

## 1. Purpose

EraseCase is an AI agent that reconstructs supplied evidence, determines whether each personal-data deletion request is complete, and produces the required findings, remediation, and verification steps.

The entire product serves **Ghost Data Still Exists**. Commercial positioning, customer acquisition, monetization, expansion plans, and unrelated sponsor challenges are excluded.

The central promise is:

> Every conclusion has evidence. Every violation has an action. Every action has a verification.

The objective is a complete, accurate, explainable submission competitive for **top five**. No ranking or hidden-answer score is guaranteed.

## 2. Competition Context and Score Ambition

The public event material advertises a 24-hour window beginning 24 October 2026 at 6:00 PM IST. The official portal cutoff was not independently confirmed. **Use 25 October, 5:00 PM IST for building and submitting.** The user manages portal deadlines and plans the interview after 6 PM. The reported additional interview allowance is user-supplied, not an independently verified official rule. [S4]

The following category weights and leaderboard observations came from the user's supplied snapshot, not a verified live leaderboard:

| Category | Maximum | Approved working ambition |
| --- | ---: | ---: |
| Chat transcript | 10 | 9 |
| AI judge interview | 30 | 26 |
| Output CSV | 30 | 28 |
| Code ZIP | 30 | 25 |
| **Total** | **100** | **88** |

Fifth place was **77.9** in that snapshot. Standings can change. The 88-point ambition is a planning objective, not an acceptance measurement, prediction, or proof of competitiveness.

The approved emphasis is balanced performance across all four categories. Output accuracy alone does not establish the overall result. Reasons behind other participants' category scores are unknown.

## 3. Builder Context and Repository

| Constraint | Approved decision |
| --- | --- |
| Build allowance | Initial allowance was nine hours; recheck the actual remaining clock at execution startup. The later interview is outside build capacity. |
| Participation | Solo, following the event format |
| Coding mode | AI-assisted, with the user's manual oversight |
| Backend preference | Python was selected during engineering planning; exact stack and pins are in ENGINEERING_BLUEPRINT.md. |
| Strengths | Backend, systems, data processing, and APIs |
| Frontend constraint | CLI/report presentation only, explicitly confirmed by the user; no web frontend. |
| Work location | Local development in the supplied fork and checkout |
| Spending | **₹0 additional spending**; maximum **$5 cumulative OpenRouter usage** from existing funded access, subject to actual balance. |
| Deployment | Optional and unnecessary for the approved submission scope |
| Git | Each verified implementation step receives its own separate commit under A1. |
| Branches | Work directly on main; do not create implementation, phase or handoff branches. |
| Model training | Excluded |

**Fork:** <https://github.com/kernelKain/hackerrank-orchestrate-october26>

**Local checkout supplied by the user:**

`/home/kernel-kain/Documents/Github/hackerrank-orchestrate-october26`

Discovery did not inspect the checkout. Prompt 1 subsequently verified the participant input shapes, representative evidence, empty implementation starters and applicable instructions. The current baseline and uncommitted work are recorded in EXECUTION_STATE.md and must be rechecked before execution.

## 4. User, Problem, and Outcome

### Scenario user and trigger

A privacy engineer reviews the supplied personal-data requests and needs to establish what actually happened, even when an existing workflow reports completion.

### Problem

Personal data can remain under historical identifiers, in secondary copies, or behind processes capable of recreating it. A status message or a search for only the latest email can miss consequential evidence. The engineer must also preserve records the supplied policy permits or requires.

### Failed workaround

Trusting operational success messages, checking only the current account, or relying on a plausible narrative leaves the actual obligations unresolved.

### Desired outcome

A defensible case conclusion with supporting evidence, complete required actions, and the prescribed verification. The reviewer can follow consequential decisions from the request through to the final answer.

Northstar Shop and its reported incident are fictional parts of the supplied scenario, not independently verified customer evidence. [S1]

## 5. Approved Product Mechanism

| Step | Product behavior |
| --- | --- |
| **1. Establish intent** | Determine what the person actually requested, including multilingual wording and explicit instructions to keep an account or its data. |
| **2. Establish identity** | Follow supported current and historical identifiers, distinguishing relevant records from unsupported matches. |
| **3. Reconstruct reality** | Examine relevant supplied evidence and establish what records and processes were doing at the requested audit time. |
| **4. Apply obligations** | Determine required treatment of records and identify supported copying, recreation, or restore risks. |
| **5. Challenge the assessment** | Seek concrete evidence that invalidates the proposed conclusion; resolve contradictions and expose unsupported claims. |
| **6. Produce the resolution** | Return the prescribed verdict and complete ordered findings, remediation, and verification with the required evidence references. |

### Defining strengths

- **Evidence reconciliation:** resolve conflicting claims using grounded identity, time, record, and policy information.
- **Obligation coverage:** account for each relevant requirement without silently interpreting skipped evidence as proof of absence.
- **Supported conclusions:** challenge assessments with concrete counterexamples, rather than generic requests to reconsider.
- **Complete resolution:** ensure that finding a problem leads to its required treatment and verification.

These are approved product capabilities to investigate and implement, not claims that the functionality already works.

### AI role

AI supports interpretation of request wording and heterogeneous evidence, including relevant relationships and contradictions. Its interpretations remain accountable to supplied evidence and policies. The approved engineering blueprint assigns model interpretation and deterministic computation their responsibilities; Prompt 2 must verify their behavior.

### Non-wrapper thesis

1. **Evidence reconciliation and provenance:** conclusions connect the person, time, relevant records, governing obligations, and supporting sources.
2. **Verification and domain-specific evaluation:** proposed conclusions and resolutions are examined against explicit deletion obligations.

An ordinary document-question-answering assistant can explain selected material. EraseCase must complete the entire prescribed case assessment and resolution. Existing privacy products also address deletion workflows; novelty of the overall category is not claimed.

## 6. Mandatory Challenge Contract

The current official statement and repository instructions remain authoritative; this packet is not a replacement for them. [S1–S3]

- Read the provided CSVs and relevant local evidence/media.
- Derive predictions only from participant-facing data; do not use hidden answers, hardcoded test labels, or filename-specific verdicts.
- Produce one row per supplied evaluation request: **518 rows**, sorted as required.
- Use the exact output schema from `problem_statement.md`: `case_id,deletion_status,steps_json`.
- Assess deletion intent, identity history, policy treatment, and resource state at `audit_at`.
- Use only permitted statuses, step fields, operations, states, evidence references, and ordering.
- Include an evaluation workflow and the required evaluation report.
- Keep the solution runnable and explain its actual requirements.

The final answer semantics include `COMPLETE`, `INCOMPLETE`, and `NOT_APPLICABLE`. A non-deletion request requires the prescribed empty action list. Completion requires both proper treatment and preservation of required retained records, without active prohibited recreation paths. [S1]

Permitted techniques are options, not extra requirements. The approved engineering blueprint now records the selected extraction, model-pilot, prompting and evaluation approach. Installation, account access and actual quality remain execution proofs for Prompt 2.

## 7. Product Boundary

### Essential

- Complete coverage of the supplied case set and relevant evidence.
- Accurate, policy-aware assessments and full required resolutions.
- Inspectable support for consequential conclusions.
- Every mandatory submission artifact and the required interview.
- Genuine development records and honest reporting of results, costs, limitations, and corrections.

### Optional

Only improvements that materially support required correctness, explainability, evaluation, or reproducibility within the available time and credits.

### Excluded

- Presentation, pitch deck, demo video, and separate demo application.
- Marketing website, extensive dashboard, animation, and further branding work.
- Commercial planning, buyers, distribution, monetization, and expansion plans.
- Live-company connections and execution of real-world deletion.
- External research or extra datasets used to answer the supplied cases.
- Integrations introduced merely because sponsor credits exist.
- Model training and unrelated prize categories.
- A separate simulation product or speculative feature that displaces mandatory work.

### Must-be-true claim

> Given the supplied requests, policies, identities, activity, and evidence, EraseCase produces the prescribed assessment and complete ordered steps for every case, reflecting the evidence at that case's audit time.

### Fallback boundary

Optional work may be removed. Required cases and evidence types cannot silently become optional. If essential interpretation is blocked, expose and resolve the gap instead of inventing a completion claim or a fourth output status.

The approved presentation fallback is simply the required output and documentation. No demonstration deliverable is needed.

## 8. Required Submission Materials

| Material | Required purpose |
| --- | --- |
| `output.csv` | Final answers for all evaluation requests |
| `code.zip` | Runnable solution, prompts, configuration, README, and required evaluation material |
| Evaluation report | Actual accuracy measurements, at least three additional evaluation cases, failures, and improvements |
| Usage report | Model identities, calls, tokens, and estimated costs for the final full-data run |
| Root `log.txt` | Development transcript following applicable repository instructions |
| AI judge interview | The user's later explanation of the actual approach, decisions, trade-offs, and evaluation; planned after 6 PM |

Reports are maintained under code/evaluation/ and copied byte-for-byte to archive-root evaluation/ during packaging to satisfy both documented path conventions. Current report files are templates with no measured results. Important explanations must appear directly in readable Markdown. Exclude credentials and prohibited archive contents. [S2]

Submitting a ZIP does not make runtime API access irrelevant: the model can be used locally to generate the submitted output. Exact execution requirements and evaluator network/credential availability remain unverified. Document actual dependencies and never include secrets. [S1–S2]

This packet is the planning handoff. The finished repository README must document the runnable solution and official requirements; it must not imply that this proposal alone is a completed implementation.

## 9. Coding Tools and Shared Interaction Log

| Role | Current approved responsibility |
| --- | --- |
| Codex | Main product, evidence/identity/policy logic, model integration, tests, debugging, evaluation, accounting and final correctness |
| Cursor | CLI/report presentation and documentation; Codex verifies final technical artifacts |

This is a planned mixed-tool workflow, replacing the earlier fallback-only policy.
The initial discovery model labels were preferences, not proof of an active runtime.
Each actual session must verify and log its own exact harness and model identifier.
Coding-tool access and the project's OpenRouter inference usage are separate.

### Required continuity

- Use the same checkout, main branch and root log.txt.
- Run only one editing harness at a time.
- Preserve earlier log entries and append genuine session/turn records.
- Maintain docs/EXECUTION_STATE.md with branch/HEAD, changed files, checks, blockers,
  budget, current unit and next permitted action.
- After every verified step and its separate commit, recommend KEEP CODEX,
  SWITCH TO CURSOR or SWITCH TO CODEX, with a reason.
- Follow the E01–E07 ownership map in ENGINEERING_BLUEPRINT.md; E07 returns to Codex before
  final checks and its commit.
- The receiving harness reads AGENTS.md, the approved handoff and current notes.
- Never fabricate another tool's work or guess its active runtime model.
- Preserve relevant sanitized traces from both tools for the separate trace export.

The official logging contract remains shared and append-only. [S3]

Mixed-tool Codex-bonus eligibility remains unverified and is not promised. [S4]

## 10. Available Resources and Spending Policy

Availability and amounts below are user-reported. Repeated offers are counted once. Current balances, redemption status, capabilities, and usable access require validation where relevant.

| Resource | Reported access | Approved treatment |
| --- | --- | --- |
| OpenRouter | User reports an API key; actual funded balance unverified | Selected runtime gateway; total project usage capped at $5 |
| Backboard | $5 credit reported during discovery | Available resource inventory; not selected for this runtime |
| LangSmith | $100 credit | Candidate evaluation/tracing resource if setup is worthwhile |
| Tinker | $10 credit | Validate suitability; training remains excluded |
| Paper Instruments | $5 credit | Capability and relevance unverified |
| Grok/API account access | User reports access; exact balance unconfirmed | Validate actual runtime API access separately from subscriptions |
| Render | $50 credit | Available if necessary; deployment not required |
| DigitalOcean | Available; amount unspecified | Available if necessary |
| Docker agentic compute | $250 credit | Additional compute only if required |
| Tavily | $25 credit | No current external-search requirement |
| Browserbase | One month Developer plan | No current browser-automation requirement |
| Toloka | $50 credit | No current external-labeling requirement |
| Tendem | $50 credit | No current human-delegation requirement |
| ElevenLabs | Creator subscription / reported offer | No audio requirement |
| .tech domain | One-year offer | No domain requirement |
| Cursor Pro, Grokbot, X Plus and other coding access | User reports access; balances unspecified | Development resources; do not assume they fund runtime inference |

The user selected OpenRouter and delegated a bounded, quality-first runtime-model choice. Usable access and balance still require execution proof. Root .env loading and Git/archive exclusions are required in E01; never paste or record the key in chat.

**Resource rule:** use resources that strengthen required correctness within the remaining time and cumulative $5 OpenRouter ceiling. No automatic purchases. Do not import unrelated sponsor conditions. Prompt 0 selected no runtime provider; the later user amendment selected OpenRouter. A small project-specific pilot selects explicit runtime models; no measured winner exists yet.

## 11. Evidence, Assumptions, and Critical Risks

| Level | What is established |
| --- | --- |
| **VERIFIED** | Public problem statement, README, logging instructions, advertised tool flexibility, and required deliverables were inspected on 25 October 2026. |
| **USER-SUPPLIED** | Fork/local path, working cutoff, nine-hour allowance, tool/model preferences, resource inventory, and leaderboard snapshot. |
| **PRELIMINARY** | Exact-name searches found no prominent EraseCase product collision on 25 October; availability is not established. Backup names: GhostSift and NullTrail. |
| **ASSUMPTION** | The approved complete solution can achieve useful reliability within available time and access. |
| **UNKNOWN** | Hidden-answer performance, final ranking, exact official cutoff, effective runtime balances, complete evidence feasibility, evaluator network access, and mixed-tool bonus eligibility. |

### Two principal risks

1. **Missing or misinterpreted evidence:** a plausible verdict can conceal an unresolved obligation. Mitigation: ground conclusions in relevant evidence and expose coverage gaps for resolution.
2. **Unbalanced submission:** good CSV output can coexist with weak code documentation, transcript, or interview explanation. Mitigation: make all required materials agree with the actual solution and measured behavior.

### Do-not-build trigger

If early execution proofs establish that essential evidence coverage is unattainable within the available time and resources, reopen feasibility and product claims before proceeding. Do not silently reduce mandatory coverage or claim a complete solution.

## 12. Engineering Blueprint and Remaining Execution Proofs

All 14 engineering sections are approved in [ENGINEERING_BLUEPRINT.md](ENGINEERING_BLUEPRINT.md). Planning
established a local Python architecture, grounded extraction/indexing, deterministic
validation, OpenRouter interpretation, A1 step execution, individual commits,
tool handovers and required packaging/reporting.

E01 completed clean dependency installation, local secret-file protection,
authenticated endpoint checks, strict-schema and synthetic-image probes, initial
contracts/storage/CLI boundaries, offline CI and 11 unit tests.

The following remain VERIFY-EARLY, rather than completed functionality:

- Reliable extraction across every essential evidence format.
- Project-specific model quality and measured cost/latency.
- Historical identity, cutoff, policy and recreation-risk regressions.
- Feasible full-run time/cost and both harnesses' trace-export routes.

Evaluation and the final audit have not run. E02–E07 require their applicable A1
authorization. No resource is added merely because a sponsor credit exists.

## 13. Decision History

| Amendment | Approved effect |
| --- | --- |
| **A01** | Restrict the product to the competition; remove commercial and nonessential scope |
| **A02** | Remove organizer branding from product notes; use README-style packet formatting; adopt the user's fork and permit meaningful commits |
| **A03** | Remove presentation, video, and separate demonstration work; retain required submission and interview |
| **A04** | Initial Codex-primary/Cursor-fallback policy; superseded by A08, while shared append-only logging remains |
| **A05** | Adopt 5 PM IST on 25 October as the user's working cutoff; emphasize actual input reading, exact output, evaluation, and no hardcoded answers |
| **A06** | Consolidate available resources and use only what materially supports the task |
| **A07** | Cap cumulative OpenRouter usage at $5; require root .env loading and Git/archive secret exclusion |
| **A08** | Codex owns core engineering/correctness; Cursor handles presentation/docs; record every tool handover |
| **A09** | A1 stepwise execution and a separate commit per verified step; its working-branch choice is superseded by A14 |
| **A10** | Focus on build/submission by 5 PM; user manages deadlines and plans the interview after 6 PM |
| **A11** | Select suitable OpenRouter runtime models through a small quality-first project pilot within $5 |
| **A12** | Confirm frontend scope means CLI and reports, with no new web interface |
| **A13** | Consolidate the complete approved engineering plan into ENGINEERING_BLUEPRINT.md; remove the separate handoff file and repair references |
| **A14** | Commit and push verified work directly to main; delete build/erasecase and create no further implementation branches |

Earlier concept lists that treated individual audit features as standalone products were superseded by one complete auditor. Elaborate simulations and presentation-led differentiation were not retained as required capabilities.

Gates A, B, D, and E are approved. Gate C's demonstration scope was removed by user instruction. The final packet is approved with the latest amendments.

## 14. Stage Boundary

**Prompt 0 is complete.**

This packet approves the product identity, scenario user, problem, desired outcome, non-technical mechanism, qualification, differentiation, required product boundary, working constraints, and handoff questions.

**Prompt 1 is complete:** all 14 engineering sections are approved in ENGINEERING_BLUEPRINT.md. Planning readiness does not establish runtime success.

**Prompt 2** owns product implementation, installation, tests, Git operations, packaging and delivery. It is not started. The latest user instruction authorizes documentation synchronization only; wait for explicit execution authorization.

The user may amend any approved decision. Later explicit instructions take precedence after their impact is reflected in the handoff. No unbuilt functionality, completed evaluation, prepared submission, or achieved score is claimed here.

## Official References

- **S1 — [Problem statement](https://github.com/interviewstreet/hackerrank-orchestrate-october26/blob/main/problem_statement.md)**
- **S2 — [Starter README and submission instructions](https://github.com/interviewstreet/hackerrank-orchestrate-october26/blob/main/README.md)**
- **S3 — [Repository agent and logging instructions](https://github.com/interviewstreet/hackerrank-orchestrate-october26/blob/main/AGENTS.md)**
- **S4 — [Public event, tools, and rewards information](https://www.hackerrank.com/hackerrank-orchestrate-october26)**
- **[Evaluation request list](https://github.com/interviewstreet/hackerrank-orchestrate-october26/blob/main/dataset/deletion_requests.csv)**
- **[Submission page](https://www.hackerrank.com/contests/hackerrank-orchestrate-october26/challenges/ghost-data-still-exists)**

Sources checked on 25 October 2026. Recheck applicable repository/source instructions at execution startup if they have changed. The user manages portal deadlines; do not repeat resolved deadline intake.
