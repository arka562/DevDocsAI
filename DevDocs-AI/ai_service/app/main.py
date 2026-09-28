from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import documents, chat

app = FastAPI(title="DevDocs AI - AI Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this in production to just your Express server
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "devdocs-ai-ai-service"}


app.include_router(documents.router, prefix="/ai", tags=["documents"])
app.include_router(chat.router, prefix="/ai", tags=["chat"])
