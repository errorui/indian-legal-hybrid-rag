# Decision-router fine-tuning data and Laya experiment

This folder owns a new 200-case fine-tuning pilot independently of the existing
100-case evaluation dataset and the main thread's inference runs.

| Split | Single-turn | Multi-turn | Search | No search | Total |
|---|---:|---:|---:|---:|---:|
| Training | 80 | 80 | 80 | 80 | 160 |
| Validation | 20 | 20 | 20 | 20 | 40 |

Each group contains a single-turn search request, a single-turn no-search
request, and two multi-turn cases with the same latest question but different
evidence coverage. All four cases remain in one split. Topics explicitly
referenced in the evaluation inputs are excluded. Train/validation article
references are also disjoint; broad template and scenario families are shared.

The histories are constructed fixtures, using opening source passages from the
existing corpus. They are not LLM-generated conversations. Labels describe
whether the required passage and source are already supplied. Unknown subjects
are labelled no-search because they require clarification first.

Each row contains `query`, `history`, `expected_route`, a rationale and provenance,
plus `request` and `target` for training. `request.state` contains only conversation
messages; policy and two candidate descriptions are in `request.questions`.
Expected labels, source provenance and rationales stay outside `request`.

The initial ModernJEV experiment design freezes the encoder and trains the existing scalar
scoring head with grouped cross-entropy over the two candidates. This dataset
creation does not execute training or change the model. Training and inference
must use the same conversation-only serializer. All complete candidate inputs
are checked against a 512-token initial budget without trimming histories.

Rebuild using the existing environment:

```powershell
.\.venv\Scripts\python.exe code/decision_benchmark/head_finetuning/build_dataset.py
```

Files under `data/`:

- `finetuning_cases.jsonl`: all 200 samples.
- `train.jsonl`: 160 optimizer-training samples.
- `validation.jsonl`: 40 checkpoint-selection and calibration samples; threshold fixed at 0.5.
- `review.md`: all questions, histories and label rationales.
- `source_excerpts.json`: original corpus provenance and rendered excerpts.
- `manifest.json`: hashes, split counts, overlap checks and token lengths.

This is a small synthetic training pilot. The existing evaluation set has already
been inspected repeatedly; use a fresh final test before claiming generalisation.

## Completed Laya experiment — 2026-10-02

The requested Laya experiment is complete in `laya_run_v2/`. It uses the pinned
`convaiinnovations/laya` checkpoint, revision
`55cf4c4ebb4ebe31b2550e8bdf3bd21b99753851`, on the RTX 3050 Laptop GPU.
Only `head.*` (the two decision transformer layers) and `scorer.*` were trained:
26,245,121 parameters. The 395,048,706 other parameters, including the
ModernBERT-large encoder, question-type embedding and act/escalate head, stayed frozen.

The run uses the same 160 training / 40 validation / 100 evaluation samples.
AdamW uses learning rate 1e-4, weight decay 0.01, micro-batch 4, accumulation 2,
gradient clipping 1.0, warmup plus cosine decay, and seed 20261002. Candidate
order is randomly chosen between two cached views for each training sample.
Training stopped after 14 epochs; epoch 10 was selected by minimum validation
cross-entropy. Validation accuracy is 55%; validation temperature is 1.5691682.
The decision threshold stays at 0.5.

| Metric | Original Laya | Fine-tuned Laya |
|---|---:|---:|
| Overall evaluation accuracy | 52% | 70% |
| Single-turn accuracy | 48% | 92% |
| Multi-turn accuracy | 56% | 48% |
| Missed searches / 50 | 45 | 11 |
| Extra searches / 50 | 3 | 19 |
| Median full routing time | 32.1 ms | 31.4 ms |

The gain comes from single-turn cases; multi-turn performance regressed and
unnecessary searches increased. This is a pilot result, not evidence of broad
generalisation or a reason to automatically replace the production router.

Peak allocated training VRAM was 639.7 MiB. The full-inference peak was 920.3
MiB; peak reserved VRAM was 1,816 MiB. Allocated and reserved memory are
different measures. Frozen parameters were hash-checked unchanged, no backbone
gradients were present, no inputs were truncated, and cached/full inference
agreed on all 40 validation decisions (maximum probability difference <0.00005).

Artifacts:

- `laya_run_v2/report.md` and `summary.json`: results and frozen-weight audit.
- `laya_run_v2/head_epoch_10.safetensors`: selected decision layers/scorer only.
- `laya_run_v2/calibration.json`: validation temperature and fixed threshold.
- `laya_run_v2/before.jsonl` and `after.jsonl`: all 100 predictions for both variants.
- `laya_run_v2/history.json`: epoch losses, accuracies, learning rates and gradient norms.
- `laya_run_v2/last.pt`: resumable model/optimizer/scheduler/RNG state.

The first attempt in `laya_run/` is superseded: its feature batch builder cast
FP32 backbone outputs to BF16. Final verification caught the mismatch. The
corrected run retrained from the original head with unchanged data and settings,
preserving the original output dtype. Its GPU-produced `laya_run/features.pt`
cache is valid and reused; other first-attempt checkpoints/results are invalid.
Head checkpoint filenames are unique per epoch to avoid Windows overwrite errors.

To reproduce in a separate local output directory, use the existing environment:

```powershell
.\.venv\Scripts\python.exe code/decision_benchmark/head_finetuning/train_laya.py --output laya_reproduction
```

The script requires CUDA BF16, uses the local pinned model, and has no CPU
inference fallback. The frozen encoder computes features once on GPU; later
head steps reuse the cached features while the encoder is offloaded to CPU.
Keep backbone outputs in their native FP32 dtype even under BF16 autocast.

Load the trained head over the original pinned model using the experiment's
`configure_model()` and `apply_head()` helpers. The decision layers/scorer stay
FP32 under BF16 autocast; set the API's `temperature_by_options['choice:2']`
to the value in `calibration.json`. Inference runs through the existing
conversation-only Laya wrapper. The production router and original snapshot
were not modified.

## Full Laya fine-tuning on Colab — 2026-10-03

Full encoder and decision-layer training was run by Raj Raman in
[the full fine-tuning Colab notebook](https://colab.research.google.com/drive/1H76Plu7j4yZlBZAbNhvpfjFkemV5iqcR#scrollTo=MCH9ULff6sKa).
The figures below were reported from that run. The notebook, full checkpoint and
100-case output files have not been independently downloaded or audited locally.

### Objective and progression

Compare a small binary decision router with the application's LLM tool calling
at the same initial `search_corpus` decision. The original 400-case, three-way
experiment was rejected and removed. Its results are not used here. The rebuilt
benchmark has 100 cases: 50 single-turn and 50 multi-turn; each style contains
25 search and 25 no-search targets. The baseline receives the tool definition
on every case; deterministic chat-only rules do not decide its route.

All systems receive the same conversation and compact evidence policy. The
local models score two options, `search` and `no_search`, with search selected
at probability >= 0.5. The state contains only conversation messages; the
policy and options are separate question fields. Gold labels, rationale and
provenance are outside the inference request. This measures the initial routing
decision, not search quality, final-answer quality or an end-to-end dialogue.

Reference histories in the 100-case benchmark are actual LLM-generated answers
grounded in corpus excerpts, replayed identically across systems. The training
and validation histories are constructed excerpt-based fixtures. Related groups
stay together, train/validation article references are disjoint, and explicitly
referenced evaluation topics are excluded. Templates and scenario families are
shared, so article separation does not make this a fully independent distribution.

The first binary inference run produced LLM 84%, ModernJEV 45%, Laya 52% and
Qwen JEV 50%. An input audit found that ModernJEV's upstream helper injected
`available_tools: []`. A conversation-only rerun corrected that serialization
while preserving policy, labels, threshold and reference histories. It reused
the identical saved LLM predictions without new provider requests. Laya and
Qwen already had conversation-only state. Corrected ModernJEV accuracy was 40%.
The original input-mismatch result is retained for audit, not treated as corrected.

### Full-training configuration

The Colab run starts from original Laya revision
`55cf4c4ebb4ebe31b2550e8bdf3bd21b99753851`, not the head-only checkpoint.
It uses the exact same 160 training / 40 validation split and unchanged 100-case
evaluation file. Dataset fingerprints are:

| File | SHA-256 |
|---|---|
| `data/train.jsonl` | `4777e05a02deca14bebb1d12b1b495cc4cf7ce575528245927b72b8c37801ae4` |
| `data/validation.jsonl` | `65f4a7d15bff68edb3b5d7a8116f1b0772b3bc1dc7da1b08dc9f62a4c93e6623` |
| `../cases.jsonl` | `7819dd08df06688ceccf8e7412849d13b236671c85c381074e9b6b9aa450c201` |

| Setting | Full Colab run |
|---|---|
| GPU | Tesla T4, 14.6 GiB available device memory reported |
| Total parameters | 421,293,827 |
| Trainable parameters | 421,029,889 |
| Frozen parameters | 263,938: unrelated act/escalate head |
| Trained modules | ModernBERT-large encoder, question-type embedding, decision layers, scorer |
| Precision | FP32 parameters; FP16 autocast with gradient scaling |
| Memory control | Encoder/head gradient checkpointing; AdamW `foreach=False` |
| Microbatch / accumulation | 2 / 4, effective batch 8 |
| Encoder / decision learning rates | 2e-5 / 1e-4 |
| Optimizer | AdamW, weight decay 0.01 |
| Schedule / clipping | 10% warmup, cosine decay; gradient norm 1.0 |
| Seed | 20261002 |
| Training cap / patience | 12 epochs / 3 epochs without validation-loss improvement |
| Selection | Minimum validation cross-entropy, improvement > 1e-4 |
| Evaluation threshold / temperature | 0.5 / 1.0; no temperature fit for this reported full run |
| Longest training input | 368 tokens, complete history retained |

T4 computation explicitly uses FP16. The initial capability check reported
BF16 through emulation; this was corrected before any training. Full training
performs live encoder forward/backward passes with `detach_encoder=False`;
it does not train over cached encoder features. Candidate order is randomized
between two tokenized views for training and fixed for validation/evaluation.

A training-step smoke test confirmed nonzero encoder gradients. Learning rate
zero preserved the starting weights while allocating optimizer state. Peak GPU
allocated/reserved memory was 6.69/7.10 GiB. Epoch training peaked near 7.11 GiB.
The 421,029,889 trainable parameters confirm this is full binary-path training;
the unrelated escalation head has no target in this dataset and remains frozen.

### Reported training logs

| Epoch | Train loss | Train accuracy | Validation loss | Validation accuracy | Single | Multi | Peak allocated GiB | Seconds* | Saved best |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 0.7540 | 63.1% | 0.2733 | 97.5% | 100% | 95% | 7.09 | 82 | Yes |
| 2 | 0.1978 | 91.9% | 0.0725 | 95% | 100% | 90% | 7.11 | 72 | Yes |
| 3 | 0.1195 | 96.9% | 0.0910 | 97.5% | 100% | 95% | 7.10 | 66 | No |
| 4 | 0.0318 | 99.4% | 0.0062 | 100% | 100% | 100% | 7.11 | 87 | Yes |
| 5 | 0.0004 | 100% | 0.0076 | 100% | 100% | 100% | 7.10 | 82 | No |
| 6 | 0.0000 | 100% | 0.0001 | 100% | 100% | 100% | 7.10 | 98 | Yes |

*Printed epoch times include checkpoint saving. Every reported epoch had zero
skipped optimizer updates. Logs after epoch 6 and the final stopping epoch were
not supplied; the reported 100-case evaluation explicitly loaded epoch 6.
Rounded training loss 0.0000 is not a claim of exact zero loss.

### Same 100-case benchmark comparison

| Model / run | Overall | Single-turn | Multi-turn | Missed searches / 50 | Unnecessary searches / 50 |
|---|---:|---:|---:|---:|---:|
| LLM tool calling | 84% | 80% | 88% | 10 | 6 |
| ModernJEV, corrected conversation-only input | 40% | 50% | 30% | 48 | 12 |
| Original Laya | 52% | 48% | 56% | 45 | 3 |
| Qwen JEV | 50% | 50% | 50% | 50 | 0 |
| Laya, head-only fine-tuning | 70% | 92% | 48% | 11 | 19 |
| **Laya, full fine-tuning: epoch 6** | **81%** | **98%** | **64%** | **7** | **12** |

The full model got 81/100 correct: single-turn 49/50 and multi-turn 32/50.
Its confusion counts are 43 true searches, 38 true no-search decisions, 7 missed
searches and 12 unnecessary searches. Of 19 errors, 18 are multi-turn: 7 missed
searches and 11 unnecessary searches. Single-turn contributes one unnecessary search.

Full fine-tuning gained 29 percentage points over original Laya and 11 points
over head-only fine-tuning. It is 3 points below LLM tool calling overall,
18 points above it on single-turn and 24 points below it on multi-turn. Three
more correct cases for the LLM is descriptive, not evidence of statistical
superiority without paired error analysis. Full-trained routing latency and
end-to-end latency were not measured in this Colab evaluation.

### Interpretation and next work

Multi-turn means the latest question depends on prior messages. It includes
“expand that” and “explain it more”, transformations of supplied facts, requests
for new evidence, and ambiguous references. The word “explain” does not itself
decide whether to search. Reuse history when it contains enough evidence; search
for missing evidence; clarify when essential context is unresolved.

Training and validation losses both declined, so these logs do not show the
classic persistent validation-loss rise of overfitting. Nevertheless, 40/40
validation versus 81/100 benchmark reveals a distribution/generalisation gap.
Shared constructed templates can make validation easier without exact duplicate
inputs or article leakage. The repeatedly inspected 100-case benchmark is a
development comparison, not a fresh final generalisation test.

Preserve epoch 6, inspect the 18 multi-turn errors before another training run,
and create independently written conversations for a fresh final evaluation.
Avoid choosing checkpoints or thresholds from these test outcomes. Production
integration is not established by this experiment.

The reported Colab output directory is `/content/laya_full_finetune/run_01`.
It contains `best_model.safetensors`, `best.json`, `last.pt`, `config.json`,
`history.json`, `best_validation_predictions.json`, `test_100_summary.json`,
`test_100_predictions.jsonl`, `test_100_predictions.csv` and
`test_100_comparison.csv`. `last.pt` stores model, optimizer, scheduler, scaler
and RNG states for epoch resumption. Colab `/content` storage is temporary;
the notebook link does not itself preserve runtime model files. Download and
archive those artifacts before the runtime is deleted.

For a future LinkedIn post, the supported headline is: **a 421M-parameter
decision router improved from 52% to 81% on our constructed 100-case legal-RAG
routing benchmark after full GPU fine-tuning; single-turn reached 98%, while
multi-turn remained the main gap at 64%.** Include the 160/40 split, LLM's 84%
comparison and benchmark limitations. Do not present 100% validation as test
accuracy or claim measured production speedups.
