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
    query: str
    top_k: int = 5

@router.post("/process-document")
async def process_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    fd, temp_path = tempfile.mkstemp(suffix=".pdf")
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(await file.read())

        raw_text = extract_text_from_pdf(temp_path)
        cleaned_text = clean_text(raw_text)
        chunks = chunk_text(cleaned_text, chunk_size=500, overlap=50)

        # Generate embeddings
        embeddings = get_embeddings_batch(chunks)
        
        # Store in FAISS
        vector_store.add_chunks(chunks, embeddings, source=file.filename)

        return {
            "filename": file.filename,
            "status": "success",
            "extracted_characters": len(raw_text),
            "chunk_count": len(chunks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/retrieve")
async def retrieve_chunks(query: SearchQuery):
    try:
        query_embedding = get_embedding(query.query)
        results = vector_store.search(query_embedding, top_k=query.top_k)
        return {"query": query.query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

