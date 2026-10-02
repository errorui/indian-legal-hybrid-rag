# Binary routing comparison

## Experiment record and fine-tuning results

The [full experiment record](head_finetuning/README.md) covers the input audit,
200-case training/validation dataset, local head-only fine-tuning, and full Laya
training on a Colab Tesla T4. On the unchanged 100-case benchmark, original Laya
scored 52%, head-only fine-tuning 70%, full fine-tuning 81%, and LLM tool calling
84%. Full-trained Laya reached 98% single-turn and 64% multi-turn. Those are
benchmark results; its separate 40-case validation accuracy was 100%.

[Full fine-tuning Colab notebook](https://colab.research.google.com/drive/1H76Plu7j4yZlBZAbNhvpfjFkemV5iqcR#scrollTo=MCH9ULff6sKa).
Full-run results were reported from Colab; the full checkpoint is not in Git.
The benchmark remains a small, constructed, repeatedly inspected development set.

100 constructed English cases, with independent evidence-policy labels:

| Style | Search | No search | Total |
|---|---:|---:|---:|
| Single-turn | 25 | 25 | 50 |
| Multi-turn | 25 | 25 | 50 |

ModernJEV, Laya and Qwen JEV run sequentially on CUDA BF16 in the existing
virtual environment. CPU inference fallback is disabled. Model and upstream
code revisions are pinned in `.cache/decision_sources/artifacts.json`.

The baseline uses the application's configured LLM, the real `search_corpus`
input schema, response parser, and LangGraph `tools_condition`. Every request
offers the tool; no Python greeting, rewrite or chat-only rules intervene.
All systems receive the same compact evidence policy and full conversation.
This controlled policy is not the longer production system prompt.

Local search probability >=0.5 means search; lower means no search.
These scores are not established calibrated confidence. Threshold, candidate
order and policy stay fixed throughout the test; no test-based model selection.

Reference histories contain actual LLM-generated answers grounded in excerpts
from the existing parent corpus. Article lookup selects reference excerpts;
it does not run the production hybrid retriever. Paired follow-ups share the
same history, with either a transformation of supplied facts or a new article.
Some histories have two messages, others four. Prior LLM answers are replayed
identically to all systems; no model-specific history trimming is allowed.
Generation provenance and source excerpts are saved but never sent as labels
or metadata during routing inference.

This evaluates only the initial tool/no-tool decision. It does not execute the
tool after the scored checkpoint, assess final answers, or simulate independent
end-to-end conversations. The small, constructed sample is diagnostic;
it is not a representative production accuracy estimate.

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe code/decision_benchmark/run.py dataset
.\.cache\decision_env\Scripts\python.exe code/decision_benchmark/run.py compare
```

`dataset` saves real reference conversations as it goes. `compare` checks that
all 100 histories fit every model before evaluation, then evaluates the remote
LLM and each local GPU model in separate processes. Predictions are resumable
only for an identical dataset and contract. All requests run sequentially.

The conversation-only rerun uses `results_conversation_only_gpu`. The original
run remains in `results_binary_gpu` with its input-mismatch audit. ModernJEV's
helper originally inserted an empty `available_tools` list; the adapter now
overrides only that serializer so the state contains conversation messages.
Laya and Qwen already used conversation-only state; they are rerun unchanged.
Policy, choices, model revisions and the 0.5 threshold remain fixed.

Rerun only local decision models and reuse the exact original LLM results:

```powershell
.\.cache\decision_env\Scripts\python.exe code/decision_benchmark/run.py decisions-only
```

This command makes no provider calls. It checks all 100 complete inputs before
each model's scoring pass and saves the conversation-only input audit.

Results include:

- `report.md`: overall and per-style metrics, every case, questions and histories.
- `all_cases.jsonl`: full inputs, rationales and every model output.
- `all_cases.csv`: compact per-case routes, probabilities, correctness and timing.
- `summary.json`: metrics, Wilson intervals and paired conversation-group bootstrap.
- `<model>.jsonl`: raw predictions, full baseline answer/tool calls, input hashes.
- `<model>-runtime.json`: hardware, revisions, timings and GPU peak memory.

Accuracy includes failed predictions as incorrect. Search recall includes
failures in its positive denominator. Warm GPU latency excludes loading and
three warmup calls; baseline latency includes network and answer generation.
A local no-search decision still needs an LLM answer call. These timings do not
establish end-to-end savings. There is one prediction per checkpoint per model;
provider sampling variability is not estimated.

The rejected 400-case three-way dataset and its results have been removed.
The comparison writes an unqualified selection manifest; production observation
remains disabled. An independent qualification and a binary worker integration
would be needed before enabling the observer.
