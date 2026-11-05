import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_model_names_come_from_env(monkeypatch):
    # Import happens after env is set, so the modules must pick these up.
    monkeypatch.setenv("EMBEDDING_MODEL", "models/test-embed")
    monkeypatch.setenv("GENERATION_MODEL", "test-generate")
    for name in list(sys.modules):
        if name.startswith("app.services.embeddings") or name.startswith("app.services.llm"):
            del sys.modules[name]
    from app.services import embeddings, llm

    assert embeddings.EMBEDDING_MODEL == "models/test-embed"
    assert llm.GENERATION_MODEL == "test-generate"
