import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.chunker import chunk_text


def test_empty_pages_returns_no_chunks():
    assert chunk_text([]) == []


def test_chunk_size_and_page_numbers():
    pages = [{"page": 3, "text": " ".join(f"w{i}" for i in range(120))}]
    chunks = chunk_text(pages, chunk_size=50, overlap=10)
    # 120 words, window 50, step 40 -> starts at 0, 40, 80 => 3 chunks
    assert len(chunks) == 3
    assert all(c["page"] == 3 for c in chunks)
    assert len(chunks[0]["text"].split()) == 50


def test_overlap_words_repeat_between_chunks():
    pages = [{"page": 1, "text": " ".join(f"w{i}" for i in range(30))}]
    chunks = chunk_text(pages, chunk_size=20, overlap=5)
    first_tail = chunks[0]["text"].split()[-5:]
    second_head = chunks[1]["text"].split()[:5]
    assert first_tail == second_head


def test_empty_page_text_skipped():
    pages = [{"page": 1, "text": ""}, {"page": 2, "text": "hello world"}]
    chunks = chunk_text(pages, chunk_size=10, overlap=2)
    assert len(chunks) == 1
    assert chunks[0]["page"] == 2
