import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routes import documents, chat

app = FastAPI(
    title="DevDocs AI - AI Service",
    description="Python AI backend for processing documents and running RAG.",
    version="1.0.0",
)

# Use a comma-separated list of explicit origins. Wildcard origins are unsafe
# with credentialed CORS and should not be used for a production deployment.
frontend_origins = [
    origin.strip()
    for origin in os.getenv("FRONTEND_URL", "http://localhost:5173").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=frontend_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
)


@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    if request.url.path.startswith("/ai"):
        api_key = request.headers.get("X-API-Key")
        expected_key = os.getenv("INTERNAL_API_KEY")
        if not expected_key:
            return JSONResponse(
                status_code=500,
                content={"detail": "Server configuration error: INTERNAL_API_KEY not set"},
            )
        if not api_key or api_key != expected_key:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized AI Service Access"})
    return await call_next(request)


app.include_router(documents.router, prefix="/ai", tags=["documents"])
app.include_router(chat.router, prefix="/ai", tags=["chat"])


@app.get("/")
def read_root():
    return {"message": "DevDocs AI Service is running. Visit /docs for the API Swagger UI."}
