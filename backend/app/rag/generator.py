
import re


def clean_answer_formatting(answer):
    """Clean HTML line breaks and excess whitespace safely."""
    if not isinstance(answer, str):
        answer = str(answer)

    # Convert HTML line breaks to regular newlines.
    answer = re.sub(r"(?i)<br\s*/?>", "\n", answer)

    # Remove trailing spaces without changing word content.
    answer = "\n".join(
        line.rstrip() for line in answer.splitlines()
    )

    # Prevent excessive blank lines.
    answer = re.sub(r"\n{3,}", "\n\n", answer)

    return answer.strip()


def generate_rag_answer(rag_prompt, llm_callable):
    """Generate an answer and clean common formatting artifacts."""
    if not rag_prompt:
        raise ValueError("RAG prompt cannot be empty.")

    if not callable(llm_callable):
        raise TypeError(
            "llm_callable must be a callable function."
        )

    answer = llm_callable(rag_prompt)
    return clean_answer_formatting(answer)
