import faiss
import numpy as np
import os
import json

# Dimension for all-MiniLM-L6-v2 is 384
DIMENSION = 384
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "vector_store")
os.makedirs(DATA_DIR, exist_ok=True)

class VectorStore:
    def __init__(self):
        self.index_path = os.path.join(DATA_DIR, "index.faiss")
        self.metadata_path = os.path.join(DATA_DIR, "metadata.json")
        
        # Load or create index
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.index = faiss.IndexFlatL2(DIMENSION)
            self.metadata = []

    def add_chunks(self, chunks: list[str], embeddings: list[list[float]], source: str):
        if not chunks:
            return
            
        vectors = np.array(embeddings).astype('float32')
        self.index.add(vectors)
        
        for chunk in chunks:
            self.metadata.append({
                "text": chunk,
                "source": source
            })
            
        # Save to disk
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, 'w') as f:
            json.load(f) if False else json.dump(self.metadata, f) # just dump

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[dict]:
        if self.index.ntotal == 0:
            return []
            
        vector = np.array([query_embedding]).astype('float32')
        distances, indices = self.index.search(vector, top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.metadata):
                results.append({
                    "text": self.metadata[idx]["text"],
                    "source": self.metadata[idx]["source"],
                    "distance": float(distances[0][i])
                })
        return results

# Singleton instance
vector_store = VectorStore()
