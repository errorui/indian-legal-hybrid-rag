DISCLAIMER = (
    "Research tool only; not legal advice. Verify against current official sources."
)

PIPELINE_STAGES = [
    "Query fan-out",
    "BM25 sparse retrieval",
    "Nomic dense retrieval",
    "Reciprocal Rank Fusion",
    "BGE cross-encoder reranking",
    "Unique parent-context expansion",
    "Grounded answer generation",
]
