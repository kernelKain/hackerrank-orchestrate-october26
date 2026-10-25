# EraseCase — Evaluation Report

Status: MEASURED offline public sample, fictional custom cases, and the frozen 518-row submission.
Blueprint: version 1.4. Runtime: local deterministic auditor. Model calls during this evaluation and the final run: 0.

Final run: `PYTHONPATH=code .venv/bin/python code/main.py run --run-dir runs/final --budget-usd 4`.
Run ID `c0c5643f2c624834b274f14c690f424b`. Elapsed 39.01 seconds. Root `output.csv` has 518 sorted rows: COMPLETE 177, INCOMPLETE 335, NOT_APPLICABLE 6. Output SHA-256 `6d28e09ea4308f2acaf4598b0c48554e858fb9ea5edd0b6d601e8d4c51f54c10`. Evidence fingerprint `4a3d1956cbeac82dc72a3e67cabe599970ac5d37db961053134c252dbfa1c82f`. `validate --input output.csv --run-dir runs/final` recomputed both fingerprints and passed. Findings cite evidence (672 cited findings). Future remediation and verification steps on incomplete cases use an empty evidence id (1,529 steps).
Measurement command: `PYTHONPATH=code .venv/bin/python -m evaluation.main --suite all --run-dir runs/evaluation --budget-usd 0`.
Public timing on this machine: 8.01 seconds to load evidence and score 32 cases. Full 518-request assessment, without writing `output.csv`: 0.59 seconds to load and 35.64 seconds to assess. Unresolved intents after the lexicon fix: 0.

Reference labels are read only by `code/evaluation/scoring.py`. `code/erasecase/` does not read `sample_output.csv`.

## Measured metrics

| Metric | Public samples (32) | Independent custom cases (5) |
| --- | --- | --- |
| Deletion-status accuracy | 32/32 (1.000) | 5/5 (1.000) |
| Exact positional step accuracy | 116/193 (0.601) | 5/5 (1.000) |
| Step precision / recall / F1 | 1.000 / 0.819 / 0.900 | 1.000 / 1.000 / 1.000 |
| Field accuracy | 960/1351 (0.711) | 1.000 |
| Exact sequence accuracy | 9/32 (0.281) | 5/5 (1.000) |
| Full-row accuracy | 9/32 (0.281) | 5/5 (1.000) |

Public multiset counts, excluding `step_no`: 158 true positives, 0 false positives, 35 false negatives. Every emitted public step matches a reference step. The 35 missing steps are omissions.

Empty-array convention: when both sequences are empty, the case is an exact sequence match and adds nothing to positional or multiset ratios. A one-sided empty sequence is a mismatch. `NOT_APPLICABLE` uses this convention.

Positional step accuracy counts a seven-field match at each index, with the denominator equal to the sum of the longer sequence length. Missing or extra positions add seven unmatched fields. Repeated use of the 32 public answers is development evidence, not an estimate of hidden-set accuracy.

## Custom cases

All subjects, emails, and resource ids below are fictional and are not rows from the participant dataset. The same `Auditor` and deletion rules assess them.

| Case | Scenario | Expected status | Actual result |
| --- | --- | --- | --- |
| CUSTOM-01 | Historical email; primary profile absent; later replica still holds that email; a post-cutoff cleanup and a same-name decoy are present | INCOMPLETE | INCOMPLETE. Only `account_1001` is cited from `custom_replica`, then delete and verify. |
| CUSTOM-02 | French/English export request that says to keep the account, while a profile exists | NOT_APPLICABLE with [] | NOT_APPLICABLE with []. |
| CUSTOM-03 | Redacted tombstone, retained security audit, anonymized analytics, disabled flow, blocked restore | COMPLETE | COMPLETE. Five evidence-backed verification steps and no findings. |
| CUSTOM-03A | CUSTOM-03 with an email left on the tombstone | INCOMPLETE | INCOMPLETE, including `REPORT_EXPOSED_PII` for `tombstone_1003`. |
| CUSTOM-03B | CUSTOM-03 with the connector enabled | INCOMPLETE | INCOMPLETE. `DISABLE_DATA_FLOW` is ordered before its verification. |
| CUSTOM-03C | CUSTOM-01 replica capture moved to after `audit_at` | COMPLETE | COMPLETE. Only the timely primary absence is verified. |
| CUSTOM-04 | A null-identifier analytics row shares the catalog but not the subject | COMPLETE | COMPLETE. The analytics resource is omitted. |
| CUSTOM-03E | The linked security-audit lookup returns zero rows | No false present verification | COMPLETE without `audit_record_1003`. Absence is not rewritten as presence. The allowed operations do not include restoring a retained record, so this gap is omitted rather than given a fabricated finding. |

CUSTOM-01 steps:

1. FINDING `account_service` `account_1001` `REPORT_REMAINING_RECORD` `PRESENT` `custom_replica`
2. REMEDIATION `account_service` `account_1001` `DELETE_RECORD` `ABSENT` evidence empty
3. VERIFICATION `account_service` `account_1001` `VERIFY_RECORD_ABSENT` `ABSENT` evidence empty

CUSTOM-03 steps:

1. VERIFICATION `security_service` `audit_record_1003` `VERIFY_RECORD_PRESENT` `PRESENT` `custom_audit`
2. VERIFICATION `account_service` `tombstone_1003` `VERIFY_RECORD_REDACTED` `REDACTED` `custom_tombstone`
3. VERIFICATION `analytics_platform` `analytics_1003` `VERIFY_RECORD_ANONYMIZED` `ANONYMIZED` `custom_analytics_done`
4. VERIFICATION `integration_service` `data_flow_1003` `VERIFY_DATA_FLOW_DISABLED` `DISABLED` `custom_flow`
5. VERIFICATION `backup_service` `backup_1003` `VERIFY_RESTORE_BLOCKED` `BLOCKED` `custom_backup`

Invalid citations are rejected by the step contract: a finding with an empty `evidence_id` does not construct.

## Case-level public results

| Case | Expected | Predicted | Sequence | Failure category |
| --- | --- | --- | --- | --- |
| case_01 | COMPLETE | COMPLETE | miss | no_supported_identifier |
| case_02 | COMPLETE | COMPLETE | miss | no_supported_identifier |
| case_03 | COMPLETE | COMPLETE | miss | no_supported_identifier |
| case_04 | COMPLETE | COMPLETE | miss | no_supported_identifier+resource_not_in_evidence |
| case_05 | COMPLETE | COMPLETE | exact | exact |
| case_06 | INCOMPLETE | INCOMPLETE | miss | no_supported_identifier |
| case_07 | INCOMPLETE | INCOMPLETE | miss | no_supported_identifier |
| case_08 | INCOMPLETE | INCOMPLETE | miss | no_supported_identifier |
| case_09 | INCOMPLETE | INCOMPLETE | miss | no_supported_identifier+only_after_cutoff |
| case_10 | INCOMPLETE | INCOMPLETE | miss | no_supported_identifier |
| case_11 | INCOMPLETE | INCOMPLETE | exact | exact |
| case_12 | COMPLETE | COMPLETE | exact | exact |
| case_13 | INCOMPLETE | INCOMPLETE | exact | exact |
| case_14 | INCOMPLETE | INCOMPLETE | exact | exact |
| case_15 | INCOMPLETE | INCOMPLETE | exact | exact |
| case_16 | INCOMPLETE | INCOMPLETE | exact | exact |
| case_17 | INCOMPLETE | INCOMPLETE | exact | exact |
| case_18 | INCOMPLETE | INCOMPLETE | miss | no_supported_identifier+resource_not_in_evidence |
| case_19 | INCOMPLETE | INCOMPLETE | exact | exact |
| case_20 | INCOMPLETE | INCOMPLETE | miss | no_supported_identifier+resource_not_in_evidence |
| case_21 | COMPLETE | COMPLETE | miss | no_supported_identifier |
| case_22 | INCOMPLETE | INCOMPLETE | miss | no_supported_identifier |
| case_23 | INCOMPLETE | INCOMPLETE | miss | no_supported_identifier+only_after_cutoff |
| case_24 | INCOMPLETE | INCOMPLETE | miss | only_after_cutoff |
| case_25 | COMPLETE | COMPLETE | miss | no_supported_identifier |
| case_26 | COMPLETE | COMPLETE | miss | no_supported_identifier |
| case_27 | COMPLETE | COMPLETE | miss | no_supported_identifier |
| case_28 | COMPLETE | COMPLETE | miss | no_supported_identifier |
| case_29 | INCOMPLETE | INCOMPLETE | miss | no_supported_identifier+only_after_cutoff |
| case_30 | INCOMPLETE | INCOMPLETE | miss | no_supported_identifier+only_after_cutoff |
| case_31 | COMPLETE | COMPLETE | miss | no_supported_identifier |
| case_32 | INCOMPLETE | INCOMPLETE | miss | no_supported_identifier |

Category counts for the 23 sequence misses: `no_supported_identifier` 15, `no_supported_identifier+only_after_cutoff` 4, `no_supported_identifier+resource_not_in_evidence` 3, `only_after_cutoff` 1. None are `linked_but_omitted` or `extra_step`.

## Failures and improvements

Intent coverage: 29 of 518 requests previously raised `UnresolvedIntent`. They use five repeated phrases: Portuguese permanent account deletion (`exclusão`), Korean permanent deletion (`삭제`), a phone correction that keeps the account active, an invoice-copy request that leaves the profile in place, and an email change that continues the service. The local lexicon now accepts the two deletion phrases and rejects the three keep/correct phrases. After the change, all 518 requests resolve locally. The public 32 were already resolved, and their sequence score stayed 9/32.

Sequence omissions: inspected cited files either do not contain the expected resource, contain it with null identifiers and no single-subject trace, or were captured after `audit_at`. Assigning those resources by report-time proximity is ambiguous across the 518 requests, because many requests share report timestamps. They stay omitted. CUSTOM-04 locks the null-identifier rule.

Retained-record absence: a linked security-audit observation with zero rows was eligible to be verified as present. It is now classified as absent and omitted. Public false positives remained 0, so this did not remove a step the public reference currently matches. The operation list still cannot say "restore this retained record," which CUSTOM-03E records as a limitation.

## Verification and limitations

Offline checks for this unit are `pytest -c code/pytest.ini code/tests` (53 passed), the evaluation command above, preflight, the final run, and `validate`. No OpenRouter call was made for the score or the 518-row run. Hidden-set accuracy is unknown. Eleven PNG evidence files remain marked `VISION_REQUIRED` and were not sent to a model. The public re-score after the final run stayed 32/32 statuses, 9/32 exact sequences, 158 matched steps, 0 extra steps, and 35 omissions.
