def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Splits text into chunks of roughly `chunk_size` tokens (approximated by words).
    Includes `overlap` words from the previous chunk.
    """
    if not text:
        return []

    words = text.split()
    chunks = []
    
    if len(words) <= chunk_size:
        return [text]

    i = 0
    while i < len(words):
        chunk = words[i:i + chunk_size]
        chunks.append(" ".join(chunk))
        i += chunk_size - overlap

    return chunks
