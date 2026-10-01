import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("LLM_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)

def get_embedding(text: str) -> list[float]:
    """
    Generates a dense vector embedding using Gemini to save RAM.
    """
    if not API_KEY:
        raise ValueError("LLM_API_KEY is missing")
    
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type="retrieval_query"
    )
    return result['embedding']

def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    Generates embeddings for a batch of texts.
    """
    if not API_KEY:
        raise ValueError("LLM_API_KEY is missing")
        
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=texts,
        task_type="retrieval_document"
    )
    return result['embedding']
