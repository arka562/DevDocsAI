"""Retrieval step of the RAG pipeline: question -> query embedding -> top-k chunks."""
import os
from typing import List, Dict, Optional
from .embeddings import embed_query
from . import vector_store

TOP_K = int(os.getenv("TOP_K", "5"))


def retrieve_chunks(user_id: str, question: str, document_ids: Optional[List[str]] = None, top_k: int = TOP_K) -> List[Dict]:
    query_vector = embed_query(question)
    return vector_store.search(user_id, query_vector, top_k=top_k, document_ids=document_ids)
