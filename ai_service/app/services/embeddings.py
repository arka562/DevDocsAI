from sentence_transformers import SentenceTransformer

# Load a lightweight pre-trained model for embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_embedding(text: str) -> list[float]:
    """
    Generates a dense vector embedding for a single string of text.
    """
    embedding = model.encode(text)
    return embedding.tolist()

def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    Generates embeddings for a batch of texts.
    """
    embeddings = model.encode(texts)
    return embeddings.tolist()
