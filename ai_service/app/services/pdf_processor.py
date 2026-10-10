import pypdf

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file using pypdf.
    """
    pages = []
    try:
        with open(file_path, "rb") as file:
            reader = pypdf.PdfReader(file)
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    pages.append({"page": i + 1, "text": page_text})
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
        raise e
    return pages
