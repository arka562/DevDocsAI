from fastapi import APIRouter, HTTPException
from ..schemas.chat import ChatRequest, ChatResponse
from ..services.rag import answer_question

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    try:
        result = answer_question(
            user_id=payload.user_id,
            question=payload.question,
            document_ids=payload.document_ids,
        )
        return ChatResponse(**result)
    except RuntimeError as e:
        # e.g. missing LLM_API_KEY
        raise HTTPException(status_code=503, detail=str(e))
