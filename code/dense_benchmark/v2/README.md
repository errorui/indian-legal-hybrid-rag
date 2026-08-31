# Dense benchmark v2

This version uses the converted evaluation suite as ground truth. Dense retrieval
still ranks the 871 child chunks; `relevant_parent_ids` documents the parent mapping,
and `relevant_child_ids` is the metric ground truth.

The runnable v2 set contains only automatically resolved mappings. Questions with
missing or ambiguous article-to-parent matches remain in the parent-level review
report and are intentionally excluded until manually checked.

From the repository root:

```powershell
.\.venv\Scripts\python.exe code\dense_benchmark\v2\prepare_v2.py
.\.venv\Scripts\python.exe code\dense_benchmark\benchmark_dense.py `
  --queries code\dense_benchmark\v2\queries.json `
  --models code\dense_benchmark\models.json `
  --output-dir code\dense_benchmark\v2\results
```

Validate without loading models:

```powershell
.\.venv\Scripts\python.exe code\dense_benchmark\benchmark_dense.py `
  --queries code\dense_benchmark\v2\queries.json --validate-only
```
