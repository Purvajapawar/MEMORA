
from sentence_transformers import CrossEncoder

from backend.app.retrieval.faiss_retriever import retrieve_documents


# Load the Cross-Encoder from the local cache only
reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2",
    local_files_only=True
)


def retrieve_reranked(query, candidate_k=50, top_k=5):
    """
    Retrieve candidates using FAISS and rerank them
    using a Cross-Encoder.
    """

    candidates = retrieve_documents(query, top_k=candidate_k)

    if not candidates:
        return []

    pairs = [
        [query, candidate["content"]]
        for candidate in candidates
    ]

    scores = reranker.predict(pairs)

    for candidate, score in zip(candidates, scores):
        candidate["rerank_score"] = float(score)

    reranked = sorted(
        candidates,
        key=lambda x: x["rerank_score"],
        reverse=True
    )

    for rank, candidate in enumerate(reranked[:top_k], start=1):
        candidate["final_rank"] = rank

    return reranked[:top_k]
