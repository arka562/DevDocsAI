from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag import run_rag_pipeline

router = APIRouter()

class MessageHistory(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    question: str
    history: list[MessageHistory] = []

@router.post("/chat")
async def chat_with_docs(request: ChatRequest):
    """
    RAG Endpoint: Answers a question based on uploaded documentation.
    """
    if not request.question:
        raise HTTPException(status_code=400, detail="Question is required")
        
    try:
        # Convert Pydantic models to dicts for the service layer
        history_dicts = [{"role": msg.role, "content": msg.content} for msg in request.history]
        response = run_rag_pipeline(request.question, history_dicts)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
