from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import documents, chat

app = FastAPI(
    title="DevDocs AI - AI Service",
    description="Python AI backend for processing documents and running RAG.",
    version="1.0.0"
)

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev only, restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router, prefix="/ai", tags=["documents"])
app.include_router(chat.router, prefix="/ai", tags=["chat"])

@app.get("/")
def read_root():
    return {"message": "DevDocs AI Service is running. Visit /docs for the API Swagger UI."}
