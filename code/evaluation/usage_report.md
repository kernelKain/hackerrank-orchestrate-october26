# EraseCase — Usage Report

Status: final 518-row run measured. No provider was called.
Blueprint: version 1.4.
Final output/run ID/time: run `c0c5643f2c624834b274f14c690f424b`, 39.01 seconds, 518 rows.
Output fingerprint: `6d28e09ea4308f2acaf4598b0c48554e858fb9ea5edd0b6d601e8d4c51f54c10`.
Evidence fingerprint: `4a3d1956cbeac82dc72a3e67cabe599970ac5d37db961053134c252dbfa1c82f`.
Cumulative approved OpenRouter ceiling: $5, subject to actual funded balance. Funded balance remains unverified.

Coding-assistant development usage is not application inference. The final run made no application model calls.

## Final-run provider and model totals

| Provider / exact returned model | Calls / attempts | Input tokens | Output tokens | Total tokens | Charged / estimated USD |
| --- | --- | --- | --- | --- | --- |
| No provider called | 0 / 0 | 0 | 0 | 0 | 0 |
| Overall | 0 / 0 | 0 | 0 | 0 | 0 |

## Totals and per-request averages

| Quantity | Value |
| --- | --- |
| Expected evaluation requests | 518 |
| Actually completed requests | 518 |
| Final-run input/output/total tokens | 0 / 0 / 0 |
| Average tokens per request | 0 |
| Total final-run charged/estimated cost | 0 |
| Average cost per request | 0 |
| Calls, failed/retried attempts and cache hits | 0 / 0 / 0 |

## Preparation, model selection and cached work

E01 measured charges, preserved here:

| Call | Requested model | Returned provider path | Charged USD |
| --- | --- | --- | --- |
| Strict-schema semantic probe | openai/gpt-6.1-sol | OpenAI | 0.000218 |
| Synthetic-image vision probe | google/gemini-3.8-flash | Google AI Studio | 0.0012525 |
| Measured E01 total | | | 0.0014705 |

A first schema attempt stopped before vision and has a conservative uncertain reservation of at most $0.005056. Conservative cumulative exposure is at most $0.0065265. Ceiling remainder is at least $4.9934735. These figures are not reset by E05.

E05 project-model comparison was not executed. Before the lexicon fix, 29 requests were locally unresolved, but they collapse to five clear deletion or non-deletion phrases. After the fix, a full local pass resolved all 518 request texts with zero `UnresolvedIntent` results. The public sample remained 32/32 on status. Spending the evaluation allocation to ask both semantic candidates about phrases the local rules now decide would not change a plan, a citation, or an operation. No winner is selected because the decision path does not call a model. The E01 probes remain the capability evidence. A later visual shortcoming, if one is measured, is the trigger for another paid check.

E05 offline evaluation and the frozen final run made 0 calls, used 0 tokens, and added $0. The run store records 94 extractions, 7,847 observations, 4,011 activity links, and 4,556 identity facts. `model_calls` in that store is 0.

## Failures and reconciliation

No final-run provider timeout, retry, or missing usage field occurred, because no provider was called. The E01 uncertain reservation stays pending and is not treated as zero. `require_known_cost` rejects a missing charge instead of coercing it to $0. Validation recomputed the output hash and re-hashed all 94 evidence files; both matched the manifest.

## Runtime model selection

No project-specific production model is selected. Intent, policy, order, and serialization stay in code. Candidate IDs remain `openai/gpt-6.1-sol`, `anthropic/claude-sonnet-5.5`, and `google/gemini-3.8-flash`.

## Release forecast

The frozen run completed 518 assessments in 39.01 seconds, with 0 unresolved intents, 0 model calls, and $0 charged. Status counts are COMPLETE 177, INCOMPLETE 335, and NOT_APPLICABLE 6.

Eleven PNGs stayed `VISION_REQUIRED`. The run made `vision_calls=0` and did not apply the E01 image-probe price to them. Hidden-set accuracy is not forecast.

## Verification

The accounting guard is `code/tests/test_evaluation.py::test_missing_provider_cost_is_not_zero`. The evaluation command records `model_calls=0` in `runs/evaluation/metrics.json`. No credential, authorization header, or raw provider body is stored in this report.
