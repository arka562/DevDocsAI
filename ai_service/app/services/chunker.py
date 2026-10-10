def chunk_text(pages: list[dict], chunk_size: int = 500, overlap: int = 50) -> list[dict]:
    """
    Splits page texts into chunks of roughly `chunk_size` words.
    Includes `overlap` words from the previous chunk.
    Returns list of dicts: {"text": str, "page": int}
    """
    if not pages:
        return []

    chunks = []
    
    for page in pages:
        words = page["text"].split()
        if not words:
            continue
            
        i = 0
        while i < len(words):
            chunk_words = words[i:i + chunk_size]
            chunks.append({
                "text": " ".join(chunk_words),
                "page": page["page"]
            })
            i += chunk_size - overlap

    return chunks
