
from backend.app.rag.context_builder import build_rag_context
from backend.app.rag.prompt import build_rag_prompt
from backend.app.rag.generator import generate_rag_answer
from backend.app.rag.llm_provider import groq_llm
from backend.app.rag.verifier import verify_answer


INSUFFICIENT_EVIDENCE_MESSAGE = (
    "I could not verify a sufficiently supported answer from "
    "MEMORA's retrieved knowledge. Please review the sources "
    "or refine your question."
)


def answer_query(query):
    """
    Complete MEMORA query pipeline.

    Query -> Retrieval -> Reranking -> RAG Context
    -> Grounded Prompt -> Groq Answer -> Verification
    -> Safe Final Response
    """

    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    query = query.strip()

    # 1. Retrieve and rerank evidence
    rag_context = build_rag_context(
        query=query,
        candidate_k=50,
        top_k=5
    )

    # 2. Build the evidence-grounded prompt
    rag_prompt = build_rag_prompt(rag_context)

    # 3. Generate the answer
    answer = generate_rag_answer(rag_prompt, groq_llm)

    # 4. Verify factual support and contextual relevance
    verification = verify_answer(
        answer,
        rag_context,
        groq_llm
    )

    verified = verification["verified"]

    # 5. Only expose the generated answer as the final answer
    # when the verifier accepts it. Keep the draft separately
    # for debugging if verification rejects it.
    final_answer = answer if verified else INSUFFICIENT_EVIDENCE_MESSAGE

    return {
        "query": query,
        "answer": final_answer,
        "verified": verified,
        "verification_confidence": verification["confidence"],
        "verification_reason": verification["reason"],
        "sources": rag_context["sources"],
        "num_sources": rag_context["num_sources"],
        "partial_answer": None if verified else answer
    }
