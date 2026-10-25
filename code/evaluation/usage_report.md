# EraseCase — Usage Report

Status: final 518-row run measured. Screenshot reading called `google/gemini-3.8-flash`.
Blueprint: version 1.4.
Final output/run ID/time: run `bf9de008cf6f42dc9245c62fd4cd2b10`, 38.39 seconds, 518 rows.
Output fingerprint: `5c75a2763b3a0ee6902b53fd2d5bc173e006a1504ff518bf54a2ef179c1bdce8`.
Evidence fingerprint: `4a3d1956cbeac82dc72a3e67cabe599970ac5d37db961053134c252dbfa1c82f`.
Cumulative approved OpenRouter ceiling: $5, subject to actual funded balance. Funded balance remains unverified.

Coding-assistant development usage is not application inference. Intent, policy, order, and serialization stay in code. The model only reads screenshots and may abstain.

## Final-run provider and model totals

| Provider / exact returned model | Calls / attempts | Input tokens | Output tokens | Total tokens | Charged / estimated USD |
| --- | --- | --- | --- | --- | --- |
| Google AI Studio / google/gemini-3.8-flash | 11 / 12 | 17676 | 14808 | 32484 | 0.068787 |
| Overall | 11 / 12 | 17676 | 14808 | 32484 | 0.068787 |

The twelfth attempt stopped at the token limit before its JSON completed. It cost $0.004107 (1,551 input tokens and 785 output tokens) and was not cached. The 11 completed readings cost $0.06468 (16,125 input tokens and 14,023 output tokens).

## Totals and per-request averages

| Quantity | Value |
| --- | --- |
| Expected evaluation requests | 518 |
| Actually completed requests | 518 |
| Final-run input/output/total tokens | 17676 / 14808 / 32484 |
| Average tokens per request | 62.71 |
| Total final-run charged/estimated cost | 0.068787 |
| Average cost per request | 0.0001328 |
| Calls, failed/retried attempts and cache hits | 11 / 1 / 0 |

## Preparation, model selection and cached work

E01 measured charges, preserved here:

| Call | Requested model | Returned provider path | Charged USD |
| --- | --- | --- | --- |
| Strict-schema semantic probe | openai/gpt-6.1-sol | OpenAI | 0.000218 |
| Synthetic-image vision probe | google/gemini-3.8-flash | Google AI Studio | 0.0012525 |
| Measured E01 total | | | 0.0014705 |

A first schema attempt stopped before vision and has a conservative uncertain reservation of at most $0.005056. Measured E01 cost is $0.0014705. The screenshot pass added $0.068787. Measured project cost is $0.0702575. With the uncertain reservation, conservative exposure is at most $0.0753135, leaving at least $4.9246865 of the ceiling. These figures are not reset by later units.

E05 project-model comparison was not executed. Before the lexicon fix, 29 requests were locally unresolved, but they collapse to five clear deletion or non-deletion phrases. After the fix, a full local pass resolved all 518 request texts with zero `UnresolvedIntent` results. The public sample remained 32/32 on status. Spending the evaluation allocation to ask both semantic candidates about phrases the local rules now decide would not change a plan, a citation, or an operation. No winner is selected because the decision path does not call a model. The E01 probes remain the capability evidence. A later visual shortcoming, if one is measured, is the trigger for another paid check.

E05 offline evaluation and the frozen final run made 0 calls, used 0 tokens, and added $0. The run store records 94 extractions, 7,847 observations, 4,011 activity links, and 4,556 identity facts. `model_calls` in that store is 0.

## Failures and reconciliation

No final-run provider timeout or missing usage field was coerced to zero. One screen reading stopped at the token limit, was discarded, and is included in the charged total above. `require_known_cost` rejects a missing charge instead of coercing it to $0. Validation recomputed the output hash and re-hashed all 94 evidence files; both matched the manifest.

## Runtime model selection

No project-specific model chooses the audit steps. Screenshot reading uses `google/gemini-3.8-flash`. Candidate IDs remain `openai/gpt-6.1-sol`, `anthropic/claude-sonnet-5.5`, and `google/gemini-3.8-flash`.

## Release forecast

The frozen run completed 518 assessments in 38.39 seconds, with 0 unresolved intents, 11 completed screen readings, 1 discarded attempt, and $0.068787 charged for those readings. Status counts are COMPLETE 169, INCOMPLETE 343, and NOT_APPLICABLE 6.

Four PNGs abstained. Seven PNGs contributed 15 observations, and 8 cases cite one of those screenshots. Hidden-set accuracy is not forecast.

## Verification

The accounting guard is `code/tests/test_evaluation.py::test_missing_provider_cost_is_not_zero`. The evaluation command records `model_calls=0` in `runs/evaluation/metrics.json`. No credential, authorization header, or raw provider body is stored in this report.
