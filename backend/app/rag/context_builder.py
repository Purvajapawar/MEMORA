from backend.app.retrieval.reranker import retrieve_reranked


def build_rag_context(
    query,
    candidate_k=50,
    top_k=5,
    max_chars_per_chunk=3000
):
    """
    Build structured RAG context from reranked MEMORA evidence.
    """

    results = retrieve_reranked(
        query,
        candidate_k=candidate_k,
        top_k=top_k
    )

    sources = []

    for i, result in enumerate(results, start=1):
        content = str(result["content"])

        if len(content) > max_chars_per_chunk:
            content = content[:max_chars_per_chunk] + "..."

        sources.append({
            "evidence_id": f"Evidence {i}",
            "doc_id": result["doc_id"],
            "chunk_id": result["chunk_id"],
            "title": result["title"],
            "source_type": result["source_type"],
            "rerank_score": result["rerank_score"],
            "content": content
        })

    return {
        "query": query,
        "context": sources,
        "sources": sources,
        "num_sources": len(sources)
    }