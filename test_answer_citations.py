
import re

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

valid_ids = {
    source["evidence_id"]
    for source in context["sources"]
}

# Simulate a generated answer with citations.
mock_answer = (
    "Backup readiness must be confirmed before the upgrade "
    "[Evidence 1]. The enterprise checklist defines the "
    "required go/no-go checks [Evidence 2]."
)

citations = re.findall(
    r"\[Evidence\s+\d+\]",
    mock_answer
)

invalid_citations = [
    citation
    for citation in citations
    if citation[1:-1] not in valid_ids
]

print("\n--- FINAL ANSWER CITATION TEST ---")
print("Mock answer:", mock_answer)
print("Citations found:", citations)
print("Invalid citations:", invalid_citations)

assert citations, "FAIL: No citations found."
assert not invalid_citations, "FAIL: Invalid evidence citation."

print("\nPASS: All answer citations refer to retrieved evidence IDs.")
