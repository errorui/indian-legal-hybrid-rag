# Indian Legal Hybrid RAG

An extensible hybrid retrieval-augmented generation system for Indian legal
documents. The current corpus is the **Constitution of India (as on 1 May
2024)**, with the retrieval pipeline designed to support additional statutes,
regulations, judgments, and other legal sources in the future.

The project combines lexical and semantic retrieval, rank fusion, neural
reranking, and parent-child context expansion to retrieve legally relevant
sections without relying on a single search method.

> **Status:** Active research and development. The retrieval and evaluation
> workflows are functional but are still being modularized and calibrated.

## Why Hybrid Retrieval?

Legal queries often mix:

- Exact references such as article numbers, schedules, amendments, and legal
  terminology.
- Semantic questions whose wording differs from the source document.
- Multi-part questions that require evidence from multiple constitutional
  provisions.

Sparse retrieval is effective for exact legal terms, while dense retrieval
captures semantic similarity. This project combines both signals and then
reranks the fused candidates before expanding the selected child chunks to
their larger parent sections.

## Pipeline

```mermaid
flowchart LR
    A["Legal PDF"] --> B["MinerU OCR and layout extraction"]
    B --> C["Heading-aware parent chunks"]
    C --> D["Semantic child chunks"]
    D --> E["BM25 sparse retrieval"]
    D --> F["Nomic embeddings and FAISS HNSW"]
    E --> G["Reciprocal Rank Fusion"]
    F --> G
    G --> H["BGE cross-encoder reranking"]
    H --> I["Parent-context expansion"]
    I --> J["Optional query fan-out and grounded generation"]
```

### 1. Document extraction

The source PDF is processed with
[MinerU](https://github.com/opendatalab/MinerU) to preserve headings, lists,
tables, and page-level layout information. The extraction command and Colab
workflow are documented in `code/pdfocr.py`.

### 2. Parent-child chunking

- `code/chunking_parent.py` builds larger parent chunks from the processed
  Markdown structure.
- `code/semantic-children.ipynb` divides parents into smaller semantic child
  chunks.
- Each child stores its parent ID, document ID, heading path, block type, text,
  and dense embedding.

This hierarchy is particularly useful for legal documents. An individual
article, clause, explanation, proviso, exception, or table may contain the
exact language needed to match a query, but its legal meaning often depends on
the surrounding section. Splitting only into large chunks can weaken retrieval
precision, while returning only small isolated chunks can remove qualifications
and context that change how a provision should be interpreted.

The child chunks provide focused retrieval units for matching specific legal
language, article references, and semantic concepts. After a relevant child is
selected, its parent ID is used to recover the broader provision and its
surrounding context. Heading paths and block types preserve structural signals,
help distinguish prose from lists or tables, and make the retrieved material
easier to trace back to its place in the source document.

This design separates **retrieval precision** from **context completeness**:
search operates on compact child chunks, while downstream reranking and
generation can use the larger parent section to reduce context loss and avoid
presenting a clause without its related conditions or exceptions.

### 3. Sparse retrieval

A BM25-style inverted index is built over child-chunk text and heading paths.
This branch prioritizes exact article references, legal phrases, and uncommon
keywords.

### 4. Dense retrieval

Child chunks are embedded with
[`nomic-ai/nomic-embed-text-v1.5`](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5).
Normalized vectors are indexed with a FAISS HNSW index using inner-product
similarity.

### 5. Fusion and reranking

- Reciprocal Rank Fusion (RRF) combines the BM25 and dense rankings.
- [`BAAI/bge-reranker-base`](https://huggingface.co/BAAI/bge-reranker-base)
  reranks the fused candidates with a cross-encoder.
- High-scoring child chunks are mapped back to their parent sections for
  context expansion.

### 6. Query fan-out and generation

`code/hybridrag.ipynb` includes an optional **evaluation-driven,
doctrine-aware query expansion** stage for multi-hop legal questions. This
approach was introduced after retrieval evaluation exposed a vocabulary gap:
users may ask about legal concepts such as the *Doctrine of Eclipse*, *Pith
and Substance*, *Severability*, or the *Basic Structure Doctrine*, while those
exact doctrine names may not appear in the constitutional text being
retrieved. A direct lexical or semantic search can therefore miss the
underlying articles even when the query is legally relevant.

The decomposition stage maps an implicit doctrine or multi-part question to
explicit, retrieval-oriented subqueries containing the relevant constitutional
concepts and article references. Each subquery is sent independently through
the hybrid retrieval pipeline, and the resulting evidence is combined before
generation.

A graph-based agent workflow could model this process with explicit routing,
state transitions, retries, and conditional branches. That design provides
more control for larger agent systems, but also introduces additional
implementation and operational complexity. The current fan-out approach is a
simpler alternative: it preserves the main benefit of decomposing complex
legal questions while keeping the retrieval flow easy to inspect, evaluate,
and debug.

The combined context can then be supplied to an Ollama-hosted model under an
anti-hallucination prompt that instructs the model to rely on retrieved
evidence and acknowledge when the corpus is insufficient.

The retrieval and evaluation stages do not require the generation stage.

## Repository Structure

```text
.
|-- code/
|   |-- chunking_parent.py        # Heading-aware parent chunk generation
|   |-- chunking_parent_test.py   # Parent-chunk inspection utility
|   |-- semantic-children.ipynb   # Semantic child chunking and embeddings
|   |-- hybridrag.ipynb           # Hybrid retrieval and optional generation
|   |-- hybrid_eval.ipynb         # Retrieval evaluation experiments
|   |-- pdfocr.py                 # MinerU/Colab extraction notes
|   `-- chunking.md               # Chunking strategy notes
|-- data/
|   |-- raw/                      # Source legal PDF
|   |-- extracted/auto/           # OCR and layout extraction artifacts
|   |-- processed/                # Cleaned Markdown and page markers
|   |-- chunks/                   # Parent and child chunk artifacts
|   `-- evaluation/               # Test suite and exploratory results
|-- .gitignore
|-- requirements.txt
`-- README.md
```

## Technology Stack

- **Language:** Python
- **Document processing:** MinerU, Markdown, JSON
- **Embeddings:** Sentence Transformers, Nomic Embed Text
- **Sparse retrieval:** Custom BM25 implementation
- **Vector search:** FAISS HNSW
- **Fusion:** Reciprocal Rank Fusion
- **Reranking:** BGE cross-encoder
- **Generation:** Ollama API (optional)
- **Evaluation:** Article-target retrieval test suite

## Getting Started

Python 3.10 is recommended.

### 1. Clone the repository

```bash
git clone https://github.com/errorui/indian-legal-hybrid-rag.git
cd indian-legal-hybrid-rag
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install the active notebook dependencies

```bash
pip install python-dotenv numpy faiss-cpu sentence-transformers scikit-learn transformers ollama jupyter
```

The embedding and reranking models are downloaded on first use. Some model
loading calls currently use `trust_remote_code=True`; review and pin model
revisions before production use.

### 4. Optional generation configuration

The retrieval notebooks can run without generation credentials. To use the
hosted Ollama generation workflow, create a local `.env` file:

```env
OLLAMA_API_KEY=your_key_here
```

The `.env` file is excluded from Git.

## Running the Workflow

Generate parent chunks:

```bash
python code/chunking_parent.py
```

Generate semantic child chunks:

```bash
cd code
jupyter notebook semantic-children.ipynb
```

Run hybrid retrieval and optional generation:

```bash
jupyter notebook hybridrag.ipynb
```

Run retrieval evaluation:

```bash
jupyter notebook hybrid_eval.ipynb
```

The evaluation experiments are also available on
[Kaggle](https://www.kaggle.com/code/rajraman83/hybrid-legal-rag-test?scriptVersionId=338881809).

## Evaluation

The current evaluation suite associates legal questions with expected
constitutional article references. The exploratory evaluator checks whether
the retrieved parent context covers the target articles.

Planned evaluation improvements include:

- Recall@K, Precision@K, MRR, and nDCG.
- BM25-only, dense-only, fused, and reranked ablations.
- Retrieval latency and context-size measurements.
- Separate reporting for direct article questions and complex doctrinal
  questions.
- Answer-level faithfulness and citation validation.

Stored evaluation artifacts represent experiments, not a production-quality
legal benchmark.

## Roadmap

- Refactor notebook logic into reusable Python modules.
- Persist and reload the FAISS index.
- Add deterministic tests for chunking, BM25, RRF, and parent expansion.
- Return structured sources, article references, ranks, and scores.
- Calibrate reranking thresholds and long-table handling.
- Add additional Indian statutes, regulations, and judgments.
- Build a citation-aware API or user interface.
- Add automated evaluation and continuous integration.

## Responsible Use

This repository is an educational and research project. It is **not legal
advice**. Legal documents may be amended, superseded, or interpreted by later
authorities. Any retrieved provision or generated answer should be checked
against current official legal sources before use.

## Author

**Raj Raman**

- [GitHub](https://github.com/errorui)
- [LinkedIn](https://www.linkedin.com/in/raj-raman-379156283/)
