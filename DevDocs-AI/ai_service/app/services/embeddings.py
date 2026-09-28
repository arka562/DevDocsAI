"""Wraps a sentence-transformers model to turn text chunks into vectors."""
import os
from functools import lru_cache
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    # Loaded once per process and cached - loading this model is the
    # slowest part of a cold start, so we do it lazily on first use.
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def embed_texts(texts: List[str]) -> np.ndarray:
    model = get_model()
    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    return embeddings.astype("float32")


def embed_query(query: str) -> np.ndarray:
    return embed_texts([query])[0]
