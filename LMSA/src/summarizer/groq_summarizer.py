# summarizer/groq_summarizer.py

import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# =========================
# CONFIG
# =========================

DEFAULT_MODEL = "llama-3.3-70b-versatile"
_TEMPERATURE = 0.3

# Client cache (important)
_CLIENT = None


def _get_client() -> Groq:
    global _CLIENT
    if _CLIENT is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError("GROQ_API_KEY not set in environment variables")

        _CLIENT = Groq(api_key=api_key)
    return _CLIENT


def summarize_text(
    transcript_text: str,
    model: str = DEFAULT_MODEL,
    save_path: str | None = None
) -> str:
    """
    Generates a professional meeting summary using Groq LLM.
    """

    if not transcript_text.strip():
        raise ValueError("Transcript text is empty")

    client = _get_client()

    prompt = f"""
You are an AI meeting assistant.

Summarize the following meeting transcript clearly and professionally.

Provide:
1. Meeting overview (1–2 lines)
2. Key discussion points (bullet points)
3. Decisions or instructions
4. Action items (if any)

Transcript:
{transcript_text}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You generate professional meeting summaries."},
            {"role": "user", "content": prompt}
        ],
        temperature=_TEMPERATURE
    )

    summary_text = response.choices[0].message.content.strip()

    # Optional persistence
    if save_path:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_text(summary_text, encoding="utf-8")

    return summary_text
