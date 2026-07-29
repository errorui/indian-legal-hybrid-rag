# Constitution RAG

RAG experiments and generated artifacts for the Constitution of India.

## Layout

- `src/` - Python scripts for chunk generation and inspection.
- `notebooks/` - exploratory RAG, semantic chunking, and evaluation notebooks.
- `data/raw/` - original source PDF.
- `data/extracted/auto/` - generated extraction artifacts from the source PDF.
- `data/processed/` - cleaned markdown and page-marker data.
- `data/chunks/` - parent/child chunk JSON and chunk inspection outputs.
- `data/evaluation/` - test suites and evaluation results.
- `archive/code-fanout/` - previous alternate notebook/script copy retained for reference.

## Setup

The parent `rag` folder already contains a virtual environment and `requirements.txt`.
A copy of `requirements.txt` is kept here so this project can stand on its own.

```powershell
cd "C:\Users\Raj Raman\Desktop\python\rag\constitutionrag"
..\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` if you want project-local environment variables.

## Useful Commands

Generate parent chunks and the largest-parent inspection file:

```powershell
..\.venv\Scripts\python.exe src\chunking_parent.py
```

Preview the first parent chunks:

```powershell
..\.venv\Scripts\python.exe src\children_chunks.py
```
