from pydantic import BaseModel
from typing import Optional


class DocumentProcessResponse(BaseModel):
    status: str
    chunk_count: int
    document_id: str


class DocumentDeleteResponse(BaseModel):
    status: str
    document_id: str
    removed_vectors: int
