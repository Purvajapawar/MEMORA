
from backend.app.rag.verifier import verify_answer

test_context = {
    "query": "What must be completed before an enterprise upgrade?",
    "sources": [
        {
            "id": "Evidence 1",
            "title": "Upgrade Checklist",
            "content": (
                "Confirm version compatibility and backup readiness "
                "before beginning the upgrade."
            )
        }
    ]
}

unsupported_answer = (
    "The upgrade is approved for tomorrow, and no backup is required."
)


def mock_verifier_llm(prompt):
    # Simulate the verifier correctly rejecting unsupported claims.
    return (
        "VERIFIED: NO\n"
        "CONFIDENCE: HIGH\n"
        "REASON: The approval date is unsupported and the backup claim "
        "contradicts the evidence."
    )


result = verify_answer(
    unsupported_answer,
    test_context,
    mock_verifier_llm
)

print("\n--- UNSUPPORTED CLAIM TEST ---")
print(result)

assert result["verified"] is False
print("\nPASS: Unsupported answer was rejected!")
