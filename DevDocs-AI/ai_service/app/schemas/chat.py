from pydantic import BaseModel
from typing import List, Optional


class ChatRequest(BaseModel):
    user_id: str
    question: str
    document_ids: Optional[List[str]] = None


class SourceItem(BaseModel):
    document_id: str
    document_name: str
    chunk_id: str
    text: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceItem]
