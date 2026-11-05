import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from evaluation.scoring import (
    citation_correct,
    is_refusal,
    keywords_present,
    retrieval_hit,
    score_case,
    summarize,
)

CHUNKS = [
    {"text": "free plan allows 100 requests", "source": "nimbus_api_guide.pdf", "page": 2, "document_id": "d1"},
    {"text": "unrelated chunk", "source": "team_handbook.pdf", "page": 1, "document_id": "d2"},
]
CASE = {
    "id": "q02",
    "question": "free plan requests?",
    "expected_doc": "nimbus_api_guide",
    "expected_pages": [2],
    "expected_keywords": ["100", "429"],
    "no_answer": False,
}


def test_retrieval_hit_checks_doc_and_page():
    assert retrieval_hit(CHUNKS, "nimbus_api_guide", [2]) is True
    assert retrieval_hit(CHUNKS, "nimbus_api_guide", [3]) is False
    assert retrieval_hit(CHUNKS, "other_doc", [2]) is False


def test_keywords_all_must_be_present():
    assert keywords_present("It allows 100 requests, then 429.", ["100", "429"]) is True
    assert keywords_present("It allows 100 requests.", ["100", "429"]) is False


def test_citation_correct():
    sources = [{"documentName": "nimbus_api_guide.pdf", "page": 2}]
    assert citation_correct(sources, "nimbus_api_guide", [2]) is True
    assert citation_correct(sources, "nimbus_api_guide", [1]) is False


def test_full_case_pass_and_fail():
    good = score_case(CASE, CHUNKS, "100 requests per hour; error 429 after that.",
                      [{"documentName": "nimbus_api_guide.pdf", "page": 2}])
    assert good["passed"] is True
    bad = score_case(CASE, CHUNKS, "some vague answer", [])
    assert bad["passed"] is False


def test_no_answer_case_needs_refusal():
    case = {"id": "q09", "question": "price?", "no_answer": True,
            "expected_doc": None, "expected_pages": [], "expected_keywords": []}
    refused = score_case(case, [], "The documentation does not contain pricing information.", [])
    assert refused["passed"] is True
    made_up = score_case(case, [], "The Pro plan costs 20 dollars per month.", [])
    assert made_up["passed"] is False


def test_is_refusal_phrases():
    assert is_refusal("No relevant documentation found. Please upload some documents first.")
    assert not is_refusal("The limit is 100 requests per hour.")


def test_summarize_rates():
    scores = [
        {"id": "a", "no_answer": False, "retrieval_hit": True, "citation_correct": True, "passed": True},
        {"id": "b", "no_answer": False, "retrieval_hit": False, "citation_correct": False, "passed": False},
        {"id": "c", "no_answer": True, "passed": True},
    ]
    s = summarize(scores)
    assert s["overall_pass_rate"] == 0.667
    assert s["retrieval_hit_rate"] == 0.5
    assert s["no_answer_accuracy"] == 1.0
