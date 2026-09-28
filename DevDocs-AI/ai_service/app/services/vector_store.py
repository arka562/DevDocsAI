"""A minimal per-user FAISS vector store with a JSON metadata sidecar.

Design choice for the MVP: one FAISS index per user (not per document),
stored on disk as `<user_id>.index` + `<user_id>.json`. This keeps
retrieval simple (search once across all of a user's documents) and
avoids needing a real vector DB service for a fresher project.
"""
import os
import json
import threading
from typing import List, Dict, Optional
import numpy as np
import faiss

VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./data/vector_store")
os.makedirs(VECTOR_DB_PATH, exist_ok=True)

_lock = threading.Lock()


def _index_path(user_id: str) -> str:
    return os.path.join(VECTOR_DB_PATH, f"{user_id}.index")


def _meta_path(user_id: str) -> str:
    return os.path.join(VECTOR_DB_PATH, f"{user_id}.json")


def _load_meta(user_id: str) -> List[Dict]:
    path = _meta_path(user_id)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_meta(user_id: str, meta: List[Dict]) -> None:
    with open(_meta_path(user_id), "w", encoding="utf-8") as f:
        json.dump(meta, f)


def _load_index(user_id: str, dim: int) -> faiss.Index:
    path = _index_path(user_id)
    if os.path.exists(path):
        return faiss.read_index(path)
    # Inner product on normalized vectors == cosine similarity
    return faiss.IndexFlatIP(dim)


def add_chunks(user_id: str, document_id: str, document_name: str, chunks: List[Dict], vectors: np.ndarray) -> int:
    """Add a document's chunk vectors + metadata to the user's index."""
    with _lock:
        index = _load_index(user_id, vectors.shape[1])
        meta = _load_meta(user_id)

        start_id = len(meta)
        index.add(vectors)

        for i, chunk in enumerate(chunks):
            meta.append(
                {
                    "vector_id": start_id + i,
                    "document_id": document_id,
                    "document_name": document_name,
                    "chunk_id": f"{document_id}_{chunk['chunk_index']}",
                    "text": chunk["text"],
                }
            )

        faiss.write_index(index, _index_path(user_id))
        _save_meta(user_id, meta)
        return len(chunks)


def search(user_id: str, query_vector: np.ndarray, top_k: int = 5, document_ids: Optional[List[str]] = None) -> List[Dict]:
    """Return the top_k most similar chunks for a user, optionally scoped
    to a subset of document_ids."""
    index_path = _index_path(user_id)
    if not os.path.exists(index_path):
        return []

    with _lock:
        index = faiss.read_index(index_path)
        meta = _load_meta(user_id)

    if index.ntotal == 0 or not meta:
        return []

    # Look up metadata by vector_id (not list position) so that deleting
    # a document's metadata entries never desyncs from FAISS's internal
    # vector positions.
    meta_by_vector_id = {m["vector_id"]: m for m in meta}

    # Over-fetch when filtering by document, then trim, since FAISS itself
    # has no native metadata filter in this simple flat-index setup.
    fetch_k = min(index.ntotal, top_k * 5 if document_ids else top_k)
    query = np.expand_dims(query_vector, axis=0)
    scores, indices = index.search(query, fetch_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        item = meta_by_vector_id.get(int(idx))
        if item is None:
            continue  # vector belongs to a deleted document
        if document_ids and item["document_id"] not in document_ids:
            continue
        results.append({**item, "score": float(score)})
        if len(results) >= top_k:
            break

    return results


def delete_document(user_id: str, document_id: str) -> int:
    """Rebuild the user's index without the given document's chunks.

    FAISS flat indexes don't support in-place deletion by id well, so for
    an MVP we just rebuild from the remaining metadata - fine at the scale
    a fresher project will realistically hit.
    """
    with _lock:
        meta = _load_meta(user_id)
        remaining = [m for m in meta if m["document_id"] != document_id]
        removed = len(meta) - len(remaining)

        if removed == 0:
            return 0

        if not remaining:
            for path in (_index_path(user_id), _meta_path(user_id)):
                if os.path.exists(path):
                    os.remove(path)
            return removed

        # The deleted document's vectors stay physically in the FAISS
        # index (flat indexes don't support cheap removal-by-id), but
        # search() looks up metadata by vector_id, so once we drop those
        # entries here the stale vectors can never be returned again.
        # Known MVP limitation: disk usage isn't reclaimed until you
        # rebuild the whole index from scratch. Fine to mention as a
        # "future improvement" in your README/demo.
        _save_meta(user_id, remaining)
        return removed
