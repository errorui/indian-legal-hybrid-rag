DISCLAIMER = (
    "Research tool only; verify important claims against authoritative sources."
)

PIPELINE_STAGES = [
    "Query fan-out",
    "BM25 sparse retrieval",
    "Dense retrieval",
    "Reciprocal Rank Fusion",
    "Cross-encoder reranking",
    "Unique parent-context expansion",
    "Grounded answer generation",
]
