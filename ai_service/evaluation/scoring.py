"""Pure scoring helpers for the DevDocs AI evaluation.

These functions take plain data (retrieved chunks, answer text, sources)
and return booleans, so they can be unit-tested without any API key.
The runner (run_evaluation.py) feeds them live pipeline output.
"""

REFUSAL_PHRASES = [
    "does not contain",
    "do not contain",
    "not contain enough information",
    "no relevant documentation",
    "couldn't find",
    "could not find",
    "not mentioned",
    "no information",
    "unable to find",
    "not available in",
    "doesn't contain",
]


def retrieval_hit(retrieved: list[dict], expected_doc: str | None, expected_pages: list[int]) -> bool:
    """True if any retrieved chunk comes from the expected doc and page."""
    if not expected_doc:
        return False
    for chunk in retrieved:
        source = str(chunk.get("source", ""))
        if expected_doc in source and chunk.get("page") in expected_pages:
            return True
    return False


def keywords_present(answer: str, expected_keywords: list[str]) -> bool:
    """All expected keywords must appear in the answer (case-insensitive)."""
    if not expected_keywords:
        return True
    text = (answer or "").lower()
    return all(k.lower() in text for k in expected_keywords)


def citation_correct(sources: list[dict], expected_doc: str | None, expected_pages: list[int]) -> bool:
    """True if the returned sources include the expected doc and page."""
    if not expected_doc:
        return False
    for src in sources or []:
        name = str(src.get("documentName", ""))
        if expected_doc in name and src.get("page") in expected_pages:
            return True
    return False


def is_refusal(answer: str) -> bool:
    """True if the answer clearly says the docs do not contain the answer."""
    text = (answer or "").lower()
    return any(phrase in text for phrase in REFUSAL_PHRASES)


def score_case(case: dict, retrieved: list[dict], answer: str, sources: list[dict]) -> dict:
    """Score one golden case. no_answer cases pass only on a refusal."""
    if case.get("no_answer"):
        refused = is_refusal(answer)
        return {
            "id": case["id"],
            "no_answer": True,
            "refused": refused,
            "passed": refused,
        }
    hit = retrieval_hit(retrieved, case.get("expected_doc"), case.get("expected_pages", []))
    kw = keywords_present(answer, case.get("expected_keywords", []))
    cite = citation_correct(sources, case.get("expected_doc"), case.get("expected_pages", []))
    return {
        "id": case["id"],
        "no_answer": False,
        "retrieval_hit": hit,
        "keywords_present": kw,
        "citation_correct": cite,
        "passed": hit and kw and cite,
    }


def summarize(scores: list[dict]) -> dict:
    total = len(scores)
    answerable = [s for s in scores if not s["no_answer"]]
    no_answer = [s for s in scores if s["no_answer"]]
    return {
        "total_cases": total,
        "passed": sum(1 for s in scores if s["passed"]),
        "overall_pass_rate": round(sum(1 for s in scores if s["passed"]) / total, 3) if total else 0,
        "retrieval_hit_rate": round(
            sum(1 for s in answerable if s["retrieval_hit"]) / len(answerable), 3
        ) if answerable else 0,
        "citation_accuracy": round(
            sum(1 for s in answerable if s["citation_correct"]) / len(answerable), 3
        ) if answerable else 0,
        "no_answer_accuracy": round(
            sum(1 for s in no_answer if s["passed"]) / len(no_answer), 3
        ) if no_answer else 0,
    }
