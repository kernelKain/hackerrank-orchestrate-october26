# EraseCase — Usage Report

Status: E05 evaluation measured. The final 518-row run has not been executed.
Blueprint: version 1.4.
Final output/run ID/time: NOT_RUN.
Output fingerprint: NOT_RECORDED.
Cumulative approved OpenRouter ceiling: $5, subject to actual funded balance. Funded balance remains unverified.

Coding-assistant development usage is not application inference. E05 made no application model calls.

## Final-run provider and model totals

| Provider / exact returned model | Calls / attempts | Input tokens | Output tokens | Total tokens | Charged / estimated USD |
| --- | --- | --- | --- | --- | --- |
| NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN |
| Overall | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN | NOT_RUN |

## Totals and per-request averages

| Quantity | Value |
| --- | --- |
| Expected evaluation requests | 518 |
| Actually completed requests | NOT_RUN |
| Final-run input/output/total tokens | NOT_RUN |
| Average tokens per request | NOT_RUN |
| Total final-run charged/estimated cost | NOT_RUN |
| Average cost per request | NOT_RUN |
| Calls, failed/retried attempts and cache hits | NOT_RUN |

## Preparation, model selection and cached work

E01 measured charges, preserved here:

| Call | Requested model | Returned provider path | Charged USD |
| --- | --- | --- | --- |
| Strict-schema semantic probe | openai/gpt-6.1-sol | OpenAI | 0.000218 |
| Synthetic-image vision probe | google/gemini-3.8-flash | Google AI Studio | 0.0012525 |
| Measured E01 total | | | 0.0014705 |

A first schema attempt stopped before vision and has a conservative uncertain reservation of at most $0.005056. Conservative cumulative exposure is at most $0.0065265. Ceiling remainder is at least $4.9934735. These figures are not reset by E05.

E05 project-model comparison was not executed. Before the lexicon fix, 29 requests were locally unresolved, but they collapse to five clear deletion or non-deletion phrases. After the fix, a full local pass resolved all 518 request texts with zero `UnresolvedIntent` results. The public sample remained 32/32 on status. Spending the evaluation allocation to ask both semantic candidates about phrases the local rules now decide would not change a plan, a citation, or an operation. No winner is selected because the decision path does not call a model. The E01 probes remain the capability evidence. A later visual shortcoming, if one is measured, is the trigger for another paid check.

E05 offline evaluation and the 518-request timing pass made 0 calls, used 0 tokens, and added $0.

## Failures and reconciliation

No E05 provider timeout, retry, or missing usage field occurred, because no provider was called. The E01 uncertain reservation stays pending and is not treated as zero. `require_known_cost` rejects a missing charge instead of coercing it to $0.

## Runtime model selection

No project-specific production model is selected. Intent, policy, order, and serialization stay in code. Candidate IDs remain `openai/gpt-6.1-sol`, `anthropic/claude-sonnet-5.5`, and `google/gemini-3.8-flash`.

## Release forecast

Measured on this workstation after one evidence load: 518 assessments completed in 35.64 seconds, with 0 unresolved intents and 0 model calls. Load was 0.59 seconds. The deterministic full run fits the local time budget and adds no OpenRouter charge.

This forecast does not include image interpretation. E03 left 11 PNGs at `VISION_REQUIRED`. The E01 image probe cost $0.0012525. Eleven similar calls are not assumed to cost eleven times that amount; E06 must measure any vision pass it actually runs. Hidden-set accuracy is not forecast.

## Verification

The accounting guard is `code/tests/test_evaluation.py::test_missing_provider_cost_is_not_zero`. The evaluation command records `model_calls=0` in `runs/evaluation/metrics.json`. No credential, authorization header, or raw provider body is stored in this report.
