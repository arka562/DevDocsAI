from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import documents, chat

app = FastAPI(
    title="DevDocs AI - AI Service",
    description="Python AI backend for processing documents and running RAG.",
    version="1.0.0"
)

import os
from fastapi import Request
from fastapi.responses import JSONResponse

# CORS config
# Restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "*")],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    if request.url.path.startswith("/ai"):
        api_key = request.headers.get("X-API-Key")
        expected_key = os.getenv("INTERNAL_API_KEY")
        if not expected_key:
            return JSONResponse(status_code=500, content={"detail": "Server configuration error: INTERNAL_API_KEY not set"})
        if not api_key or api_key != expected_key:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized AI Service Access"})
    return await call_next(request)

# Include routers
app.include_router(documents.router, prefix="/ai", tags=["documents"])
app.include_router(chat.router, prefix="/ai", tags=["chat"])

@app.get("/")
def read_root():
    return {"message": "DevDocs AI Service is running. Visit /docs for the API Swagger UI."}
