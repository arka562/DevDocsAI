# DevDocs AI

AI-powered developer documentation assistant. Upload technical PDFs, ask
questions, get grounded answers with source citations — built with a
MERN backend and a Python FastAPI service for the RAG pipeline.

## Architecture

```
React (client) -> Express (server) -> FastAPI (ai_service) -> FAISS + LLM
                        |
                     MongoDB
```

The React frontend never talks to FastAPI directly — everything goes
through Express, which handles auth, persistence, and proxies AI calls.

## What's implemented (MVP scope)

- JWT auth (register/login)
- PDF upload -> text extraction -> cleaning -> chunking -> embeddings -> FAISS
- RAG chat with source citations
- Conversation history

Not implemented yet (see the original spec doc for the full roadmap):
document search/filtering, streaming responses, Explain Code / Explain
Error / Generate Example tools, dashboard charts.

## Running it locally

You need: Node 18+, Python 3.10+, MongoDB running locally (or Atlas), and
an API key for one LLM provider (Gemini, OpenAI, or OpenRouter).

### 1. AI service (Python)

```bash
cd ai_service
python -m venv venv
source venv/bin/activate      # venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env          # then set LLM_API_KEY and LLM_PROVIDER
uvicorn app.main:app --reload --port 8000
```

First run will download the sentence-transformers embedding model
(~90MB) — that's expected and only happens once.

### 2. Server (Node/Express)

```bash
cd server
npm install
cp .env.example .env          # set MONGO_URI, JWT_SECRET
npm run dev
```

### 3. Client (React)

```bash
cd client
npm install
cp .env.example .env
npm run dev
```

Visit http://localhost:5173, register an account, upload a PDF, wait for
its status to flip to "Ready", then ask it a question in AI Chat.

## Known MVP limitations (be upfront about these in interviews)

- One FAISS index per user (flat index, cosine similarity via normalized
  inner product) — fine at small scale, not built for millions of chunks.
- Deleting a document removes its metadata (so it can never be retrieved
  again) but doesn't shrink the underlying FAISS index file on disk until
  a full rebuild — a documented tradeoff, not a bug you didn't notice.
- No streaming responses — the full answer is generated before it's sent
  back.
- Chunking is word-count based, not a real tokenizer — close enough for
  demo purposes.
- No reranking, hybrid search, or multi-agent anything — deliberately, to
  keep this a scope you can actually finish and defend in an interview.

## Resume bullet (only claim what you actually shipped)

> Built a MERN-based developer assistant using NLP-based document
> processing, semantic embeddings and RAG to answer technical questions
> from uploaded documentation with source citations. Developed a FastAPI
> AI service for PDF extraction, chunking, vector indexing (FAISS) and
> context retrieval using Sentence Transformers.
