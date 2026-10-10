from fastapi import APIRouter, UploadFile, File, HTTPException
import os
import tempfile
from pydantic import BaseModel
from app.services.pdf_processor import extract_text_from_pdf
from app.services.text_cleaner import clean_text
from app.services.chunker import chunk_text
from app.services.embeddings import get_embeddings_batch, get_embedding
from app.services.vector_store import vector_store

router = APIRouter()

class SearchQuery(BaseModel):
    user_id: str
    query: str
    top_k: int = 5

class DeleteQuery(BaseModel):
    user_id: str
    source: str

@router.post("/process-document")
async def process_document(file: UploadFile = File(...), user_id: str = ""):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    fd, temp_path = tempfile.mkstemp(suffix=".pdf")
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(await file.read())

        raw_pages = extract_text_from_pdf(temp_path)
        cleaned_pages = [{"page": p["page"], "text": clean_text(p["text"])} for p in raw_pages]
        chunks_with_meta = chunk_text(cleaned_pages, chunk_size=500, overlap=50)

        chunks_text = [c["text"] for c in chunks_with_meta]
        embeddings = get_embeddings_batch(chunks_text)
        
        vector_store.add_chunks(user_id, chunks_with_meta, embeddings, source=file.filename)

        return {
            "filename": file.filename,
            "status": "success",
            "extracted_pages": len(raw_pages),
            "chunk_count": len(chunks_with_meta)
        }
    except Exception as e:
        print(f"Internal error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/retrieve")
async def retrieve_chunks(query: SearchQuery):
    try:
        query_embedding = get_embedding(query.query)
        results = vector_store.search(query.user_id, query_embedding, top_k=query.top_k)
        return {"query": query.query, "results": results}
    except Exception as e:
        print(f"Internal error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/delete-document")
async def delete_document(query: DeleteQuery):
    try:
        vector_store.delete_document(query.user_id, query.source)
        return {"status": "success"}
    except Exception as e:
        print(f"Internal error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

