from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime
import re

def clean_markdown(text: str) -> list[str]:
    """
    Converts markdown summary into clean paragraph blocks.
    """
    lines = text.split("\n")
    cleaned = []

    for line in lines:
        line = line.strip()
        if not line:
            cleaned.append("")
            continue

        # Remove markdown bold/headers
        line = re.sub(r"\*\*(.*?)\*\*", r"\1", line)
        line = re.sub(r"^#+\s*", "", line)

        cleaned.append(line)

    return cleaned


def generate_summary_pdf(summary_text: str):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=18,
        spaceAfter=14
    )

    header_style = ParagraphStyle(
        "Header",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=11,
        leading=15,
        spaceAfter=6
    )

    # ---- Title ----
    story.append(Paragraph("Meeting Summary", title_style))
    story.append(
        Paragraph(
            f"Generated on: {datetime.now().strftime('%d %b %Y %H:%M')}",
            styles["Italic"]
        )
    )
    story.append(Spacer(1, 0.3 * inch))

    # ---- Content ----
    blocks = clean_markdown(summary_text)

    for line in blocks:
        if line.lower() in [
            "meeting overview",
            "key discussion points",
            "decisions or instructions",
            "action items"
        ]:
            story.append(Spacer(1, 0.15 * inch))
            story.append(Paragraph(line, header_style))
        elif line:
            story.append(Paragraph(line, body_style))
        else:
            story.append(Spacer(1, 0.1 * inch))

    doc.build(story)
    buffer.seek(0)
    return buffer
