# Interpretation audit

The original predictions and threshold remain unchanged. No new model inference
or threshold selection was performed in this audit.

## Confirmed input mismatch

`contracts.make_state` contains only conversation messages. The pinned ModernJEV
helper adds a missing tool inventory as `available_tools: []`. The LLM baseline,
in contrast, receives the real `search_corpus` tool. This is a benchmark setup
mistake, not evidence that an empty inventory caused the entire accuracy gap.
Its causal impact has not been measured. A corrected shared tool inventory and
new full-input preflight are required before rerunning.

## Saved score diagnostics

| Model | Median search score, search-needed cases | Median search score, no-search cases | Ranking AUC |
|---|---:|---:|---:|
| ModernJEV | 0.3631 | 0.3347 | 0.4800 |
| Laya | 0.3189 | 0.2450 | 0.7064 |
| Qwen JEV | 0.3594 | 0.3074 | 0.7886 |

AUC is the fraction of search-needed / no-search case pairs ordered correctly
by search score, with half credit for ties. It is a diagnostic computed from
the existing test predictions; it is not a calibrated probability or a new
threshold-based accuracy measurement.

Qwen's search scores range from 0.2173 to 0.4111 across all 100 cases, so its
constant no-search outcome follows directly from the frozen 0.5 threshold.
Its scores nevertheless contain some ranking signal. A new threshold must be
chosen using separate calibration/validation data, never these 100 test cases.

## Checkpoint documentation

- [Laya](https://huggingface.co/convaiinnovations/laya) distinguishes base and
  workflow-specialized checkpoints and reports substantial fine-tuning gains.
- [Qwen JEV](https://huggingface.co/joyfox/Qwen3.5-0.8B-JEV) reports teacher
  agreement, explicitly distinguishing it from human-labelled task accuracy
  and requiring independent calibration data. It is not affiliated with JEV.

These statements concern the currently published documentation; the benchmark
itself used the immutable revisions recorded in the runtime files.

Other untested explanations include candidate wording/order sensitivity and
different adaptation to history-dependent evidence routing. GPU placement was
confirmed; the run had zero inference failures and did not trim histories.
