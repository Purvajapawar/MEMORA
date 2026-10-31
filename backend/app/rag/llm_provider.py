
import os
import time

from dotenv import load_dotenv
from groq import (
    Groq,
    RateLimitError,
    APIConnectionError,
    APITimeoutError,
    InternalServerError,
)

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY is missing. Check your .env file."
    )

client = Groq(api_key=api_key)


def groq_llm(prompt):
    """Call Groq with limited retries for temporary API errors."""

    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    max_attempts = 3

    for attempt in range(max_attempts):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=0.1,
            )

            content = response.choices[0].message.content

            if not content:
                raise ValueError("Groq returned an empty response.")

            return content.strip()

        except (
            RateLimitError,
            APIConnectionError,
            APITimeoutError,
            InternalServerError,
        ):
            if attempt == max_attempts - 1:
                raise

            time.sleep(2 ** (attempt + 1))

    raise RuntimeError("Groq request failed after retries.")
