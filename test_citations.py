
import re

from backend.app.rag.context_builder import build_rag_context
from backend.app.rag.prompt import build_rag_prompt

query = (
    "What must be completed before an enterprise "
    "Private deployment upgrade begins?"
)

context = build_rag_context(
    query=query,
    candidate_k=50,
    top_k=5
)

prompt = build_rag_prompt(context)

# Collect valid evidence identifiers from retrieved sources.
valid_ids = {
    source["evidence_id"]
    for source in context["sources"]
}

# Check that every retrieved evidence identifier appears in the prompt.
missing_from_prompt = [
    evidence_id
    for evidence_id in valid_ids
    if f"[{evidence_id}]" not in prompt
]

# Find evidence-style citations in the prompt.
prompt_citations = set(
    re.findall(r"\[Evidence \d+\]", prompt)
)

invalid_citations = prompt_citations - {
    f"[{evidence_id}]" for evidence_id in valid_ids
}

print("\n--- CITATION CONSISTENCY TEST ---")
print("Retrieved evidence IDs:", sorted(valid_ids))
print("Citations in prompt:", sorted(prompt_citations))
print("Missing evidence IDs:", missing_from_prompt)
print("Invalid evidence IDs:", invalid_citations)

assert not missing_from_prompt, "Some evidence is missing from the prompt."
assert not invalid_citations, "Prompt contains an invalid evidence ID."

print("\nPASS: Prompt evidence identifiers are consistent!")
