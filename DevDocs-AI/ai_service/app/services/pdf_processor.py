"""Extracts raw text from a PDF file, page by page, using PyMuPDF (fitz)."""
import fitz  # PyMuPDF


def extract_text_from_pdf(file_path: str) -> str:
    """Return the full extracted text of a PDF, with page breaks marked."""
    text_parts = []
    with fitz.open(file_path) as doc:
        for page_num, page in enumerate(doc, start=1):
            page_text = page.get_text("text")
            if page_text.strip():
                text_parts.append(page_text)
    return "\n\n".join(text_parts)
