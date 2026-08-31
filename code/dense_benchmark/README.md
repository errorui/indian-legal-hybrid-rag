# Dense retriever benchmark

This experiment compares dense embedding models on the same 871 Constitution child
chunks. It does not use BM25, fusion, or the cross-encoder, so the measurements isolate
the dense retriever.

The initial comparison includes:

- the current raw Nomic encoding as the baseline;
- Nomic with its retrieval prefixes;
- BGE Base English v1.5;
- E5 Base v2.

Each model re-embeds the identical document text and uses normalized cosine similarity.
Results include:

- `recall@k`: at least one relevant chunk appears in the top `k`;
- `all_recall@k`: every labeled chunk for that query appears in the top `k`;
- `mean_coverage@k`: the average fraction of required chunks recovered in the top `k`;
- mean reciprocal rank of the first relevant hit for positive queries;
- per-query first relevant rank, top retrieved chunk, and top-5 retrieved chunks;
- query latency, model-load time, and corpus-encoding time;
- negative-control top-score diagnostics for queries that intentionally have no exact support.

## Run

From the repository root:

```powershell
.\.venv\Scripts\python.exe code\dense_benchmark\benchmark_dense.py
```

Run a smaller first comparison:

```powershell
.\.venv\Scripts\python.exe code\dense_benchmark\benchmark_dense.py --only nomic-raw-baseline nomic-recommended-prefixes
```

Use `--device cuda` when CUDA is available. Model downloads use the normal Hugging Face
cache. Document embeddings are cached under `.cache/dense_benchmark`, while reports are
written to `code/dense_benchmark/results`.

Validate the benchmark set without loading models:

```powershell
.\.venv\Scripts\python.exe code\dense_benchmark\benchmark_dense.py --validate-only
```

For configured application models, the runner first reuses the immutable snapshot under
`.cache/models`. Alternative models are downloaded only when they are not already cached.
Use `--ignore-project-snapshots` when the benchmark environment has a different Sentence
Transformers version from the backend environment.

## Interpretation

Use `all_recall@10` as the primary metric for multi-hop queries and adjacent-chunk
provisions, because those cases fail if the retriever surfaces only part of the answer.
Use `recall@10` as the next check for whether the model found at least one correct
foothold. Use MRR as the tie-breaker among models with similar recall.

Negative queries are not included in recall or MRR. They exist to inspect how confidently
each model retrieves near-miss chunks for unsupported claims, such as "Money Bills can be
introduced in the Council of States" or "Article 19 is suspended during an armed-rebellion
Emergency."

## Query Design

The benchmark set now mixes four query shapes:

- exact article lookups;
- semantic paraphrases with different wording from the Constitution text;
- multi-hop comparisons that require more than one child chunk;
- negative controls and hard confusions around neighboring provisions.

Several labels intentionally include adjacent child chunks because the Constitution text
for a single article spills across chunk boundaries. Current examples include Articles
83, 108, 109, 110, 213, 249, and 357. Those cases are why `all_recall@k` and
`mean_coverage@k` matter.

The expanded set is still a working benchmark, not a final production-selection dataset.
The next useful step is to keep growing it with independently reviewed paraphrases,
longer multi-hop questions, and harder negatives before using it to justify a model
change.
