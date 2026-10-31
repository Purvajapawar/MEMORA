
import re


def _format_evidence(rag_context):
    """Convert retrieved evidence into readable, source-labelled text."""

    evidence = (
        rag_context.get("sources")
        or rag_context.get("context")
        or []
    )

    if isinstance(evidence, str):
        return evidence.strip()

    if isinstance(evidence, dict):
        evidence = [evidence]

    if not isinstance(evidence, list):
        return ""

    formatted = []

    for index, item in enumerate(evidence, start=1):
        if isinstance(item, str):
            formatted.append(item)
            continue

        if not isinstance(item, dict):
            continue

        evidence_id = item.get("evidence_id", f"Evidence {index}")
        title = item.get("title", "Unknown document")
        doc_id = item.get("doc_id", "Unknown document ID")
        source_type = item.get("source_type", "Unknown source type")
        content = item.get("content", "")

        formatted.append(
            f"[{evidence_id}]\n"
            f"Document title: {title}\n"
            f"Document ID: {doc_id}\n"
            f"Source type: {source_type}\n"
            f"Content:\n{content}"
        )

    return "\n\n".join(formatted)


def verify_answer(answer, rag_context, llm_callable):
    """
    Verify factual support and contextual relevance.

    If verification fails or the provider is unavailable,
    the answer remains unverified.
    """

    if not isinstance(answer, str) or not answer.strip():
        return {
            "verified": False,
            "confidence": "LOW",
            "reason": "Empty answer."
        }

    if not isinstance(rag_context, dict):
        return {
            "verified": False,
            "confidence": "LOW",
            "reason": "Invalid RAG context."
        }

    if not callable(llm_callable):
        return {
            "verified": False,
            "confidence": "LOW",
            "reason": "Verification provider is not callable."
        }

    query = str(rag_context.get("query", "")).strip()
    evidence = _format_evidence(rag_context)

    if not evidence:
        return {
            "verified": False,
            "confidence": "LOW",
            "reason": "No usable evidence was provided for verification."
        }

    verification_prompt = f"""
You are MEMORA's evidence-grounding and contextual verification system.

Check whether the answer is factually supported by the retrieved
evidence and relevant to the user's actual question.

USER QUESTION:
{query}

RETRIEVED EVIDENCE:
{evidence}

ANSWER TO VERIFY:
{answer}

Apply these rules:

1. FACTUAL SUPPORT
Check every material factual claim against the evidence.
Do not use outside knowledge.

2. CONTEXTUAL RELEVANCE
A fact appearing somewhere in the evidence does not automatically
make it a valid answer to the question.
Check whether it applies to the customer, organization, project,
deployment, rollout, time, and situation being asked about.

3. UNRELATED CUSTOMERS OR PROJECTS
Do not transfer customer-specific dates, approvals, configurations,
commitments, or other facts to another customer or project unless
the evidence explicitly establishes that they apply.

4. POLICY VS SPECIFIC APPROVAL
Distinguish general policies and defaults from actual customer-
approved or project-specific values.

5. PARTIAL ANSWERS
An answer may address supported parts of a question while stating
that other details are unknown. Do not reject it merely for
acknowledging missing information.

6. MISSING INFORMATION
It is acceptable to state that the retrieved evidence does not
specify a value, provided the statement is appropriately qualified.
Absence from retrieved excerpts does not prove that the fact
does not exist elsewhere.

7. EVIDENCE REFERENCES
Check that cited evidence identifiers exist and support the
claims associated with them.

8. SENSITIVE OR UNKNOWN VALUES
Never infer or invent passwords, credentials, dates, approvals,
or other missing values.

9. DECISION
Return YES only if all material claims are supported and relevant,
and statements about missing information are appropriately qualified.
Return NO if any material claim is unsupported, misleading, or
inconsistent with its context.

Return exactly this format:

VERIFIED: YES or NO
CONFIDENCE: HIGH, MEDIUM, or LOW
REASON: one short sentence explaining the decision

Do not add anything else.
"""

    try:
        result = llm_callable(verification_prompt)

        if not isinstance(result, str):
            result = str(result)

        result = result.strip()

    except Exception as exc:
        error_type = type(exc).__name__

        if error_type == "RateLimitError":
            reason = (
                "Verification unavailable because the Groq rate "
                "limit was reached. The answer remains unverified."
            )
        else:
            reason = (
                f"Verification unavailable due to {error_type}. "
                "The answer remains unverified."
            )

        return {
            "verified": False,
            "confidence": "LOW",
            "reason": reason,
        }

    verified_match = re.search(
        r"(?im)^\s*VERIFIED:\s*(YES|NO)\s*$",
        result
    )

    confidence_match = re.search(
        r"(?im)^\s*CONFIDENCE:\s*(HIGH|MEDIUM|LOW)\s*$",
        result
    )

    reason_match = re.search(
        r"(?im)^\s*REASON:\s*(.+?)\s*$",
        result
    )

    if not verified_match or not confidence_match or not reason_match:
        return {
            "verified": False,
            "confidence": "LOW",
            "reason": "Invalid verification response format."
        }

    return {
        "verified": verified_match.group(1).upper() == "YES",
        "confidence": confidence_match.group(1).upper(),
        "reason": reason_match.group(1).strip()
    }
