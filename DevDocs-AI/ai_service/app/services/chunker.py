"""Splits cleaned document text into overlapping, roughly token-sized chunks.

Uses a simple whitespace-word approximation for "tokens" rather than a
real tokenizer - good enough for an MVP and keeps this dependency-free.
"""
from typing import List, TypedDict


class Chunk(TypedDict):
    chunk_index: int
    text: str


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[Chunk]:
    words = text.split()
    if not words:
        return []

    chunks: List[Chunk] = []
    start = 0
    index = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_words = words[start:end]
        chunks.append({"chunk_index": index, "text": " ".join(chunk_words)})
        index += 1

        if end == len(words):
            break

        start = end - overlap  # step forward, keeping `overlap` words of context

    return chunks
