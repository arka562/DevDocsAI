from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("LLM_API_KEY")

client = genai.Client(api_key=API_KEY) if API_KEY else None

# Embedding model is configurable via env. Default is gemini-embedding-001:
# text-embedding-004 was retired from the Gemini API (404 on embedContent,
# verified live 2026-11-05). NOTE: changing the embedding model changes the
# vector space - indexes built with another model must be rebuilt.
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")

def get_embedding(text: str) -> list[float]:
    """
    Generates a dense vector embedding using Gemini to save RAM.
    """
    if not API_KEY:
        raise ValueError("LLM_API_KEY is missing")
    
    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY", output_dimensionality=768
        ),
    )
    return list(result.embeddings[0].values)

def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    Generates embeddings for a batch of texts.
    """
    if not API_KEY:
        raise ValueError("LLM_API_KEY is missing")
        
    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT", output_dimensionality=768
        ),
    )
    return [list(e.values) for e in result.embeddings]
