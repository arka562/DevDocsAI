
import faiss
import numpy as np
import os
import json

# Dimension for Gemini text-embedding-004 is 768
DIMENSION = 768
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "vector_store")
os.makedirs(DATA_DIR, exist_ok=True)

class VectorStore:
    def __init__(self):
        self.indexes = {}
        self.metadata = {}

    def _load_user_index(self, user_id: str):
        if user_id in self.indexes:
            return
            
        index_path = os.path.join(DATA_DIR, f"{user_id}_index.faiss")
        metadata_path = os.path.join(DATA_DIR, f"{user_id}_metadata.json")
        
        if os.path.exists(index_path):
            self.indexes[user_id] = faiss.read_index(index_path)
            with open(metadata_path, 'r') as f:
                self.metadata[user_id] = json.load(f)
        else:
            self.indexes[user_id] = faiss.IndexFlatL2(DIMENSION)
            self.metadata[user_id] = []

    def _save_user_index(self, user_id: str):
        index_path = os.path.join(DATA_DIR, f"{user_id}_index.faiss")
        metadata_path = os.path.join(DATA_DIR, f"{user_id}_metadata.json")
        faiss.write_index(self.indexes[user_id], index_path)
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata[user_id], f)

    def add_chunks(self, user_id: str, chunks: list[str], embeddings: list[list[float]], source: str):
        if not chunks:
            return
            
        self._load_user_index(user_id)
        vectors = np.array(embeddings).astype('float32')
        self.indexes[user_id].add(vectors)
        
        for chunk in chunks:
            self.metadata[user_id].append({
                "text": chunk,
                "source": source
            })
            
        self._save_user_index(user_id)

    def search(self, user_id: str, query_embedding: list[float], top_k: int = 5) -> list[dict]:
        self._load_user_index(user_id)
        
        if self.indexes[user_id].ntotal == 0:
            return []
            
        vector = np.array([query_embedding]).astype('float32')
        distances, indices = self.indexes[user_id].search(vector, top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.metadata[user_id]):
                results.append({
                    "text": self.metadata[user_id][idx]["text"],
                    "source": self.metadata[user_id][idx]["source"],
                    "distance": float(distances[0][i])
                })
        return results
        
    def delete_document(self, user_id: str, source: str):
        self._load_user_index(user_id)
        
        # FAISS doesn't support easy deletion in IndexFlatL2, so we rebuild the index
        old_metadata = self.metadata[user_id]
        
        # Keep only chunks that don't match the source
        indices_to_keep = [i for i, meta in enumerate(old_metadata) if meta["source"] != source]
        
        if len(indices_to_keep) == len(old_metadata):
            return # Nothing to delete
            
        new_metadata = [old_metadata[i] for i in indices_to_keep]
        
        # Rebuild FAISS index
        new_index = faiss.IndexFlatL2(DIMENSION)
        if new_metadata:
            # Re-extract all vectors from the old index and add them to the new index
            vectors = []
            for i in indices_to_keep:
                vec = self.indexes[user_id].reconstruct(i)
                vectors.append(vec)
            new_index.add(np.array(vectors).astype('float32'))
            
        self.indexes[user_id] = new_index
        self.metadata[user_id] = new_metadata
        self._save_user_index(user_id)

# Singleton instance
vector_store = VectorStore()
