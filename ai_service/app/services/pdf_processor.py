import pypdf

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from a PDF file using pypdf.
    """
    text = ""
    try:
        with open(file_path, "rb") as file:
            reader = pypdf.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
        raise e
    return text
