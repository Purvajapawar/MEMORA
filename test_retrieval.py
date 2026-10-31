
from backend.app.rag.context_builder import build_rag_context

query = (
    "What must be completed before an enterprise "
    "Private deployment upgrade begins?"
)

context = build_rag_context(
    query=query,
    candidate_k=50,
    top_k=5
)

print("\n--- RETRIEVAL TEST ---")
print("Query:", context["query"])
print("Number of sources:", context["num_sources"])

sources = context["sources"]

for source in sources:
    print(f"\n--- {source['evidence_id']} ---")
    print("Title:", source["title"])
    print("Document ID:", source["doc_id"])
    print("Chunk ID:", source["chunk_id"])
    print("Source type:", source["source_type"])
    print("Rerank score:", source["rerank_score"])
    print("Content:", source["content"][:500])

assert len(sources) > 0, "FAIL: No sources retrieved!"

assert all(
    source.get("evidence_id")
    and source.get("doc_id")
    and source.get("chunk_id")
    and source.get("title")
    for source in sources
), "FAIL: Required source metadata is missing!"

print("\nPASS: Retrieval and source metadata checks passed!")
