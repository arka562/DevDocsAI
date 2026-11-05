import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import app.services.vector_store as vs_module

USER = "0123456789abcdef01234567"
DOC = "0123456789abcdef01234568"
DIM = vs_module.DIMENSION


@pytest.fixture()
def store(tmp_path, monkeypatch):
    monkeypatch.setattr(vs_module, "DATA_DIR", str(tmp_path))
    return vs_module.VectorStore()


def _vec(seed):
    rng = np.random.default_rng(seed)
    return rng.random(DIM).astype("float32").tolist()


def test_invalid_user_id_rejected(store):
    with pytest.raises(ValueError):
        store.search("../etc/passwd", _vec(1))


def test_add_and_search_returns_chunk(store):
    chunks = [{"text": "faiss is a vector library", "page": 2}]
    store.add_chunks(USER, chunks, [_vec(7)], source="guide.pdf", document_id=DOC)
    results = store.search(USER, _vec(7), top_k=5)
    assert len(results) == 1
    assert results[0]["text"] == "faiss is a vector library"
    assert results[0]["page"] == 2
    assert results[0]["document_id"] == DOC


def test_empty_index_search_returns_empty(store):
    assert store.search(USER, _vec(3), top_k=5) == []


def test_delete_document_removes_only_that_doc(store):
    store.add_chunks(USER, [{"text": "doc A", "page": 1}], [_vec(1)], "a.pdf", DOC)
    other = "0123456789abcdef01234569"
    store.add_chunks(USER, [{"text": "doc B", "page": 1}], [_vec(2)], "b.pdf", other)
    store.delete_document(USER, DOC)
    texts = [r["text"] for r in store.search(USER, _vec(2), top_k=5)]
    assert texts == ["doc B"]
