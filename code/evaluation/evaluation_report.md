# EraseCase — Evaluation Report

Status: TEMPLATE — evaluation has not run.
Blueprint: version 1.2, all 14 sections approved; implementation is ON HOLD.
Runtime source/configuration fingerprint: NOT_RECORDED.
Evaluation run ID/time: NOT_RUN.

This is a documentation template. It contains no measured accuracy, passing test
claim, generated prediction or hidden-answer estimate. Populate it from actual
E05/E06 results before submission. Follow the [approved engineering blueprint](../../docs/ENGINEERING_BLUEPRINT.md).
Prompt 1 is complete; report population remains E05/E06 work.

## Measured metrics

| Metric | Public samples (32) | Participant-created cases |
| --- | --- | --- |
| Deletion-status accuracy | NOT_RUN | NOT_RUN |
| Exact positional step accuracy | NOT_RUN | NOT_RUN |
| Step precision / recall / F1 | NOT_RUN | NOT_RUN |
| Field accuracy | NOT_RUN | NOT_RUN |
| Exact sequence accuracy | NOT_RUN | NOT_RUN |
| Full-row accuracy | NOT_RUN | NOT_RUN |

Definitions: status matches per case; positional exact seven-field step matches
over summed maximum sequence lengths; multiset step precision/recall/F1 excluding
step_no; positional field matches with missing/extra steps penalized; exact ordered
arrays for sequence accuracy; status plus exact array for full-row accuracy.
Document empty-array conventions and evaluator checks when implemented.

The 32/32 public-status and exact-sequence objectives are targets, not results.
Repeated use of public answers is development evidence, not an unbiased estimate
of hidden-set performance. Only the evaluator reads reference labels.

## Planned custom cases

Fixture data and full expected step sequences are pending E05 implementation.

| Case | Planned scenario | Expected status | Actual result |
| --- | --- | --- | --- |
| CUSTOM-01 | Historical email; clean primary; surviving replica; later cleanup excluded; same-name decoy | INCOMPLETE | NOT_RUN |
| CUSTOM-02 | Multilingual export request explicitly keeping the account | NOT_APPLICABLE with [] | NOT_RUN |
| CUSTOM-03 | Compliant tombstone, required retention, proper redaction/anonymization, disabled flow and blocked restore | COMPLETE | NOT_RUN |

Include the fictional inputs, evidence facts, complete expected ordered outputs,
actual outputs and rationale directly in this Markdown report when executed.
Add mutation regressions for exposed tombstone PII, missing retained records,
active recreation paths, cutoff changes and invalid citations.

## Case-level results

NOT_RUN. Add a readable row per evaluated case: case ID, expected/predicted status,
step/field results, sequence/full-row result and failure category. Do not include
unnecessary identifiers or rely only on raw data files.

## Failures and improvements

NOT_RUN. Record the concrete failure, supporting evidence, correction, affected
tests and before/after measurements. Do not claim planned fixes as completed.

## Verification and limitations

No application tests, live probes or evaluation commands have run.
Record actual commands, exit results, source/prompt/model configuration and
mocked versus live behavior. Hidden-set accuracy remains unknown.
Reconcile the final report with the source/configuration used for output.csv.
