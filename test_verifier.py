
from backend.app.rag.verifier import verify_answer


def fake_llm(prompt):
    """Simulate a verifier that detects an unsupported answer."""
    return (
        "VERIFIED: NO\n"
        "CONFIDENCE: HIGH\n"
        "REASON: The answer contains a claim not supported by the evidence."
    )


# Evidence does not contain any salary information.
rag_context = {
    "context": (
        "The documents describe model rollout procedures "
        "and customer communication requirements."
    )
}

# This answer deliberately introduces an unsupported claim.
unsupported_answer = (
    "The CEO of MEMORA earns $500,000 per year."
)

result = verify_answer(
    unsupported_answer,
    rag_context,
    fake_llm
)

print("Verifier test result:")
print(result)

# Assertions: fail the test if verification behaves incorrectly.
assert result["verified"] is False, (
    "FAIL: Unsupported answer was incorrectly accepted."
)

assert result["confidence"] == "HIGH", (
    "FAIL: Verification confidence was not parsed correctly."
)

assert "not supported" in result["reason"].lower(), (
    "FAIL: Verification reason was not parsed correctly."
)

print("\nPASS: Unsupported answer was rejected correctly!")
