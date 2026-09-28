import re

def clean_text(text: str) -> str:
    """
    Cleans raw text extracted from PDF.
    - Removes excessive newlines
    - Removes excessive spaces
    - Strips leading/trailing whitespace
    """
    if not text:
        return ""
        
    # Replace multiple newlines with a single space or newline based on context
    # Here we'll just normalize them to single spaces to keep sentences intact
    # since PDF extraction often breaks lines mid-sentence.
    text = re.sub(r'\n+', ' ', text)
    
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Optional: Remove non-printable characters or very weird artifacts
    # text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    
    return text.strip()
