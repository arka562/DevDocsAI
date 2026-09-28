import os
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from ..schemas.document import DocumentProcessResponse, DocumentDeleteResponse
from ..services.pdf_processor import extract_text_from_pdf
from ..services.text_cleaner import clean_text
from ..services.chunker import chunk_text
from ..services.embeddings import embed_texts
from ..services import vector_store

router = APIRouter()

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))


@router.post("/process-document", response_model=DocumentProcessResponse)
async def process_document(
    document_id: str = Form(...),
    user_id: str = Form(...),
    title: str = Form(...),
    file: UploadFile = File(...),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported in this version")

    tmp_dir = os.path.join("data", "documents")
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_path = os.path.join(tmp_dir, f"{document_id}.pdf")

    contents = await file.read()
    with open(tmp_path, "wb") as f:
        f.write(contents)

    # The raw PDF is kept on disk under data/documents/ (not deleted here)
    # so it can be re-chunked later with different settings if needed.
    raw_text = extract_text_from_pdf(tmp_path)
    cleaned = clean_text(raw_text)

    if not cleaned:
        raise HTTPException(status_code=422, detail="No extractable text found in this PDF")

    chunks = chunk_text(cleaned, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
    if not chunks:
        raise HTTPException(status_code=422, detail="Document produced no chunks after cleaning")

    vectors = embed_texts([c["text"] for c in chunks])
    added = vector_store.add_chunks(
        user_id=user_id,
        document_id=document_id,
        document_name=title,
        chunks=chunks,
        vectors=vectors,
    )

    return DocumentProcessResponse(status="completed", chunk_count=added, document_id=document_id)


@router.delete("/documents/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(document_id: str, user_id: str):
    removed = vector_store.delete_document(user_id, document_id)

    tmp_path = os.path.join("data", "documents", f"{document_id}.pdf")
    if os.path.exists(tmp_path):
        os.remove(tmp_path)

    return DocumentDeleteResponse(status="deleted", document_id=document_id, removed_vectors=removed)
