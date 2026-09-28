"""Ties retrieval + prompt construction + generation together."""
from typing import List, Dict, Optional
from .retriever import retrieve_chunks
from .llm import generate_answer

PROMPT_TEMPLATE = """You are DevDocs AI, a developer documentation assistant.

Answer the user's question using ONLY the provided documentation context.
If the answer cannot be found in the context, clearly state that the
documentation does not contain enough information to answer.

Documentation Context:
{context}

Question:
{question}

Provide:
1. A clear, direct explanation
2. A short code example if relevant
"""


def build_context(chunks: List[Dict]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, start=1):
        parts.append(f"[{i}] Source: {chunk['document_name']}\n{chunk['text']}")
    return "\n\n".join(parts)


def answer_question(user_id: str, question: str, document_ids: Optional[List[str]] = None) -> Dict:
    chunks = retrieve_chunks(user_id, question, document_ids=document_ids)

    if not chunks:
        return {
            "answer": (
                "I couldn't find any processed documents to search. Upload a document and "
                "wait for it to finish processing, then ask again."
            ),
            "sources": [],
        }

    context = build_context(chunks)
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)

    answer = generate_answer(prompt)

    sources = [
        {
            "document_id": c["document_id"],
            "document_name": c["document_name"],
            "chunk_id": c["chunk_id"],
            "text": c["text"][:300],
        }
        for c in chunks
    ]

    return {"answer": answer, "sources": sources}
