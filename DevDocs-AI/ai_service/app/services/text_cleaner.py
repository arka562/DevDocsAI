"""Light cleanup of extracted PDF text before chunking.

Kept deliberately simple: collapse whitespace, drop empty lines, strip
common PDF extraction artifacts (repeated headers/footers are NOT handled
here on purpose - that's a v2 improvement, not an MVP requirement).
"""
import re


def clean_text(raw_text: str) -> str:
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")

    # Collapse 3+ blank lines into a single blank line
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Collapse runs of horizontal whitespace
    text = re.sub(r"[ \t]{2,}", " ", text)

    # Drop lines that are just page numbers or stray punctuation
    lines = [ln for ln in text.split("\n") if not re.fullmatch(r"\s*[\d\-–•.]{0,4}\s*", ln)]

    return "\n".join(lines).strip()
