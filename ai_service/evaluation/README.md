# DevDocs AI — Evaluation

A golden-dataset evaluation for the RAG pipeline. It exists so quality is a
number, not a feeling.

## What is measured

For each case in `golden_dataset.json`, against two sample documents in
`sample_docs/` (all facts are invented, so the expected answers are known
exactly):

- **Retrieval hit** — did the top-5 retrieved chunks include the expected
  document and page?
- **Grounded keywords** — does the generated answer contain the facts it
  should (all expected keywords)?
- **Citation accuracy** — do the returned sources point at the right
  document and page?
- **No-answer accuracy** — for questions the documents cannot answer
  (3 of the 11 cases), did the system refuse instead of inventing an answer?

## Run it

Needs the real Gemini key in `ai_service/.env` (`LLM_API_KEY`), because it
exercises the real embeddings and generation.

```bash
cd ai_service
python -m evaluation.run_evaluation
```

Output: a console scorecard plus `evaluation/results.json` with per-case
details. The scoring logic itself lives in `scoring.py` and is unit-tested
(`tests/test_evaluation_scoring.py`) without needing a key.

## Grow the dataset

Every real failure found in manual testing becomes a new case here, so the
same mistake cannot silently come back.
