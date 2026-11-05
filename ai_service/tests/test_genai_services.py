"""Tests for the google-genai based embedding and generation services.

No real API key is used: a fake client stands in for genai.Client and
records the calls, so these tests pin down HOW the services talk to the
new SDK — model name from env, task types, 768 output dimensions (the
FAISS index size), and the values/text unwrapping.
"""

from types import SimpleNamespace

import pytest

from app.services import embeddings, llm


class FakeModels:
    def __init__(self):
        self.calls = []

    def embed_content(self, model, contents, config):
        self.calls.append(("embed", model, contents, config))
        if isinstance(contents, list):
            vectors = [[float(i)] * 4 for i in range(len(contents))]
        else:
            vectors = [[0.5] * 4]
        return SimpleNamespace(
            embeddings=[SimpleNamespace(values=v) for v in vectors]
        )

    def generate_content(self, model, contents):
        self.calls.append(("generate", model, contents, None))
        return SimpleNamespace(text="Answer grounded in the context.")


@pytest.fixture
def fake_models(monkeypatch):
    models = FakeModels()
    client = SimpleNamespace(models=models)
    monkeypatch.setattr(embeddings, "client", client)
    monkeypatch.setattr(embeddings, "API_KEY", "test-key")
    monkeypatch.setattr(llm, "client", client)
    monkeypatch.setattr(llm, "API_KEY", "test-key")
    return models


def test_single_embedding_uses_query_task_type(fake_models):
    vec = embeddings.get_embedding("how do I authenticate?")
    assert vec == [0.5] * 4
    kind, model, contents, config = fake_models.calls[0]
    assert kind == "embed"
    assert model == embeddings.EMBEDDING_MODEL
    assert config.task_type == "RETRIEVAL_QUERY"
    # The FAISS indexes are built at 768 dimensions; keep the pin.
    assert config.output_dimensionality == 768


def test_batch_embeddings_use_document_task_type(fake_models):
    vecs = embeddings.get_embeddings_batch(["chunk one", "chunk two"])
    assert vecs == [[0.0] * 4, [1.0] * 4]
    kind, model, contents, config = fake_models.calls[0]
    assert contents == ["chunk one", "chunk two"]
    assert config.task_type == "RETRIEVAL_DOCUMENT"


def test_embedding_without_key_raises(monkeypatch):
    monkeypatch.setattr(embeddings, "API_KEY", "")
    with pytest.raises(ValueError):
        embeddings.get_embedding("anything")


def test_generate_answer_returns_text_and_uses_env_model(fake_models):
    answer = llm.generate_answer("What is Nimbus?", ["Nimbus is a cloud API."])
    assert answer == "Answer grounded in the context."
    kind, model, contents, _ = fake_models.calls[0]
    assert kind == "generate"
    assert model == llm.GENERATION_MODEL
    assert "Nimbus is a cloud API." in contents
    assert "What is Nimbus?" in contents


def test_generate_answer_without_key_returns_error(monkeypatch):
    monkeypatch.setattr(llm, "API_KEY", "")
    assert "LLM_API_KEY is not set" in llm.generate_answer("q", ["ctx"])
