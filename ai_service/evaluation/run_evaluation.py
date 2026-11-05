"""Run the DevDocs AI golden-dataset evaluation against the live RAG pipeline.

What it does:
  1. Indexes the two sample documents (evaluation/sample_docs/*.txt) into a
     throwaway per-user FAISS index, using the real chunker + embeddings.
  2. For every case in golden_dataset.json it runs the real pipeline and
     scores: retrieval hit (right doc+page in top-k), keywords grounded in
     the answer, citation correctness, and refusal on no-answer cases.
  3. Prints a scorecard and writes results.json next to this file.

Requires: LLM_API_KEY in ai_service/.env (the real Gemini key).
Run from the ai_service directory:

    python -m evaluation.run_evaluation
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.chunker import chunk_text
from app.services.embeddings import get_embedding, get_embeddings_batch
from app.services.rag import run_rag_pipeline
from app.services.vector_store import vector_store
from evaluation.scoring import score_case, summarize

HERE = os.path.dirname(__file__)
# Fixed throwaway identities (valid 24-hex ObjectId shapes) — evaluation only.
EVAL_USER = "eeeeeeeeeeeeeeeeeeeeee01"
DOC_IDS = {
    "nimbus_api_guide": "eeeeeeeeeeeeeeeeeeeeee11",
    "team_handbook": "eeeeeeeeeeeeeeeeeeeeee12",
}
PAGE_SEP = "---PAGE---"


def load_pages(path: str) -> list[dict]:
    """Split a sample .txt into pages on the ---PAGE--- separator."""
    text = open(path, encoding="utf-8").read()
    parts = text.split(PAGE_SEP)
    return [{"page": i + 1, "text": part.strip()} for i, part in enumerate(parts) if part.strip()]


def index_sample_docs():
    for doc_key, doc_id in DOC_IDS.items():
        # Idempotent for re-runs: drop any earlier copy of this eval doc.
        vector_store.delete_document(EVAL_USER, doc_id)
        pages = load_pages(os.path.join(HERE, "sample_docs", f"{doc_key}.txt"))
        chunks = chunk_text(pages)
        embeddings = get_embeddings_batch([c["text"] for c in chunks])
        vector_store.add_chunks(EVAL_USER, chunks, embeddings, source=f"{doc_key}.pdf", document_id=doc_id)
        print(f"indexed {doc_key}: {len(chunks)} chunks from {len(pages)} pages")


def main():
    with open(os.path.join(HERE, "golden_dataset.json"), encoding="utf-8") as f:
        dataset = json.load(f)

    index_sample_docs()

    scores = []
    for case in dataset["cases"]:
        q_emb = get_embedding(case["question"])
        retrieved = vector_store.search(EVAL_USER, q_emb, top_k=5)
        result = run_rag_pipeline(EVAL_USER, case["question"], history=[])
        score = score_case(case, retrieved, result.get("answer", ""), result.get("sources", []))
        score["question"] = case["question"]
        scores.append(score)
        print(f"{'PASS' if score['passed'] else 'FAIL'}  {score['id']}  {case['question'][:70]}")

    summary = summarize(scores)
    out = {"summary": summary, "cases": scores}
    with open(os.path.join(HERE, "results.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print("\n=== SCORECARD ===")
    for key, value in summary.items():
        print(f"{key}: {value}")
    print("\nFull details: evaluation/results.json")


if __name__ == "__main__":
    main()
