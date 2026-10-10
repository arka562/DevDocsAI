from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
import os
import re
import tempfile
from app.services.pdf_processor import extract_text_from_pdf
from app.services.text_cleaner import clean_text
from app.services.chunker import chunk_text
from app.services.embeddings import get_embeddings_batch, get_embedding
from app.services.vector_store import vector_store

router = APIRouter()
OBJECT_ID_PATTERN = re.compile(r"^[a-fA-F0-9]{24}$")
# Keep this aligned with the Express/Multer upload limit (10 MiB).
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))
UPLOAD_READ_CHUNK_BYTES = 1024 * 1024


class SearchQuery(BaseModel):
    user_id: str = Field(..., pattern=r"^[a-fA-F0-9]{24}$")
    query: str = Field(..., min_length=1, max_length=4000)
    top_k: int = Field(default=5, ge=1, le=20)


class DeleteQuery(BaseModel):
    user_id: str = Field(..., pattern=r"^[a-fA-F0-9]{24}$")
    document_id: str = Field(..., pattern=r"^[a-fA-F0-9]{24}$")


@router.post("/process-document")
async def process_document(file: UploadFile = File(...), user_id: str = "", document_id: str = ""):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    if not OBJECT_ID_PATTERN.fullmatch(user_id) or not OBJECT_ID_PATTERN.fullmatch(document_id):
        raise HTTPException(status_code=400, detail="Valid user_id and document_id are required")
    if MAX_UPLOAD_BYTES <= 0:
        raise HTTPException(status_code=500, detail="Upload size limit is not configured correctly")

    fd, temp_path = tempfile.mkstemp(suffix=".pdf")
    total_bytes = 0
    try:
        with os.fdopen(fd, "wb") as output:
            while True:
                chunk = await file.read(UPLOAD_READ_CHUNK_BYTES)
                if not chunk:
                    break
                total_bytes += len(chunk)
                if total_bytes > MAX_UPLOAD_BYTES:
                    raise HTTPException(status_code=413, detail="PDF exceeds the maximum upload size")
                output.write(chunk)

        if total_bytes == 0:
            raise HTTPException(status_code=400, detail="Uploaded PDF is empty")

        raw_pages = extract_text_from_pdf(temp_path)
        cleaned_pages = [{"page": p["page"], "text": clean_text(p["text"])} for p in raw_pages]
        chunks_with_meta = chunk_text(cleaned_pages, chunk_size=500, overlap=50)

        chunks_text = [chunk["text"] for chunk in chunks_with_meta]
        embeddings = get_embeddings_batch(chunks_text)
        vector_store.add_chunks(
            user_id, chunks_with_meta, embeddings,
            source=os.path.basename(file.filename), document_id=document_id,
        )

        return {
            "filename": os.path.basename(file.filename),
            "status": "success",
            "extracted_pages": len(raw_pages),
            "chunk_count": len(chunks_with_meta),
        }
    except HTTPException:
        raise
    except Exception as exc:
        print(f"Document processing failed: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="Document processing failed") from exc
    finally:
        await file.close()
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/retrieve")
async def retrieve_chunks(query: SearchQuery):
    try:
        query_embedding = get_embedding(query.query)
        results = vector_store.search(query.user_id, query_embedding, top_k=query.top_k)
        return {"query": query.query, "results": results}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        print(f"Retrieval failed: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="Retrieval failed") from exc


@router.post("/delete-document")
async def delete_document(query: DeleteQuery):
    try:
        vector_store.delete_document(query.user_id, query.document_id)
        return {"status": "success"}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        print(f"Document deletion failed: {type(exc).__name__}: {exc}")
        raise HTTPException(status_code=500, detail="Document deletion failed") from exc
