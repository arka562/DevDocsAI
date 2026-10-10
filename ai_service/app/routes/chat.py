from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.rag import run_rag_pipeline

router = APIRouter()


class MessageHistory(BaseModel):
    role: str = Field(..., pattern=r"^(user|assistant)$")
    content: str = Field(..., max_length=4000)


class ChatRequest(BaseModel):
    user_id: str = Field(..., pattern=r"^[a-fA-F0-9]{24}$")
    question: str = Field(..., min_length=1, max_length=4000)
    history: list[MessageHistory] = Field(default_factory=list, max_length=4)


@router.post("/chat")
async def chat_with_docs(request: ChatRequest):
    """Answer a question based on the authenticated user's uploaded documentation."""
    try:
        history_dicts = [{"role": msg.role, "content": msg.content} for msg in request.history]
        response = run_rag_pipeline(request.user_id, request.question, history_dicts)
        return response
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid chat request") from exc
    except Exception as exc:
        print(f"Chat request failed: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="Unable to generate an answer right now") from exc
