from backend.app.rag.verifier import verify_answer


def fake_llm_yes(prompt):
    return (
        "VERIFIED: YES\n"
        "CONFIDENCE: HIGH\n"
        "REASON: The answer is supported by the evidence."
    )


def fake_llm_no(prompt):
    return (
        "VERIFIED: NO\n"
        "CONFIDENCE: HIGH\n"
        "REASON: The answer contains a claim not supported by the evidence."
    )


def check(name, answer, evidence, llm, expected):
    result = verify_answer(answer, {"context": evidence}, llm)
    passed = result["verified"] is expected

    print(f"{name}: {'PASS' if passed else 'FAIL'}")
    print(f"  Verified: {result['verified']}")
    print(f"  Confidence: {result['confidence']}")
    print(f"  Reason: {result['reason']}")

    return passed


def main():
    evidence = (
        "Dedicated customers must be notified at least "
        "5 business days before a model rollout."
    )

    tests = [
        (
            "Supported answer",
            "Dedicated customers need 5 business days' notice.",
            evidence,
            fake_llm_yes,
            True,
        ),
        (
            "Unsupported answer",
            "The CEO earns $500,000 per year.",
            evidence,
            fake_llm_no,
            False,
        ),
        (
            "Partial answer with unsupported claim",
            "Notice is 5 business days. The CEO earns $500,000.",
            evidence,
            fake_llm_no,
            False,
        ),
        (
            "Conflicting evidence",
            "The approved window is Monday at 9 AM.",
            "Document A says Monday at 9 AM. Document B says Tuesday at 10 AM.",
            fake_llm_no,
            False,
        ),
    ]

    passed = sum(check(*test) for test in tests)

    print(f"\nTests passed: {passed}/{len(tests)}")

    if passed != len(tests):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
