import re

def clean_markdown_text(text: str) -> str:
    """
    Removes markdown syntax for email/plain-text usage.
    """
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)   # bold
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)  # headers
    text = re.sub(r"^\*\s*", "- ", text, flags=re.MULTILINE)  # bullets
    return text.strip()