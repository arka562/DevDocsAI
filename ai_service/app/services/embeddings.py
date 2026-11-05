from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("LLM_API_KEY")

client = genai.Client(api_key=API_KEY) if API_KEY else None

# Embedding model is configurable via env; default matches the model the
# project has been running with. README documents this variable.
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-004")

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
