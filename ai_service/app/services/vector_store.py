import faiss
import numpy as np
import os
import json
import threading
import re

# Dimension for Gemini text-embedding-004 is 768
DIMENSION = 768
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "vector_store")
os.makedirs(DATA_DIR, exist_ok=True)

class VectorStore:
    def __init__(self):
        self.indexes = {}
        self.metadata = {}
        self.locks = {}
        self.global_lock = threading.Lock()

    def _sanitize(self, user_id: str) -> str:
        # Prevent path traversal by only allowing alphanumeric and dashes
        return re.sub(r'[^a-zA-Z0-9-]', '', user_id)

    def _get_lock(self, user_id: str):
        with self.global_lock:
            if user_id not in self.locks:
                self.locks[user_id] = threading.Lock()
            return self.locks[user_id]

    def _load_user_index(self, user_id: str):
        safe_id = self._sanitize(user_id)
        if safe_id in self.indexes:
            return
            
        index_path = os.path.join(DATA_DIR, f"{safe_id}_index.faiss")
        metadata_path = os.path.join(DATA_DIR, f"{safe_id}_metadata.json")
        
        if os.path.exists(index_path):
            self.indexes[safe_id] = faiss.read_index(index_path)
            with open(metadata_path, 'r') as f:
                self.metadata[safe_id] = json.load(f)
        else:
            self.indexes[safe_id] = faiss.IndexFlatL2(DIMENSION)
            self.metadata[safe_id] = []

    def _save_user_index(self, user_id: str):
        safe_id = self._sanitize(user_id)
        index_path = os.path.join(DATA_DIR, f"{safe_id}_index.faiss")
        metadata_path = os.path.join(DATA_DIR, f"{safe_id}_metadata.json")
        faiss.write_index(self.indexes[safe_id], index_path)
        with open(metadata_path, 'w') as f:
            json.dump(self.metadata[safe_id], f)

    def add_chunks(self, user_id: str, chunks: list[dict], embeddings: list[list[float]], source: str, document_id: str):
        if not chunks:
            return
            
        safe_id = self._sanitize(user_id)
        with self._get_lock(safe_id):
            self._load_user_index(safe_id)
            vectors = np.array(embeddings).astype('float32')
            self.indexes[safe_id].add(vectors)
            
            for chunk in chunks:
                self.metadata[safe_id].append({
                    "text": chunk["text"],
                    "page": chunk["page"],
                    "source": source,
                    "document_id": document_id
                })
                
            self._save_user_index(safe_id)

    def search(self, user_id: str, query_embedding: list[float], top_k: int = 5) -> list[dict]:
        safe_id = self._sanitize(user_id)
        with self._get_lock(safe_id):
            self._load_user_index(safe_id)
            
            if self.indexes[safe_id].ntotal == 0:
                return []
                
            vector = np.array([query_embedding]).astype('float32')
            distances, indices = self.indexes[safe_id].search(vector, top_k)
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx != -1 and idx < len(self.metadata[safe_id]):
                    meta = self.metadata[safe_id][idx]
                    results.append({
                        "text": meta["text"],
                        "source": meta["source"],
                        "document_id": meta.get("document_id", ""),
                        "page": meta.get("page", "?"),
                        "distance": float(distances[0][i])
                    })
            return results
            
    def delete_document(self, user_id: str, document_id: str):
        safe_id = self._sanitize(user_id)
        with self._get_lock(safe_id):
            self._load_user_index(safe_id)
            
            old_metadata = self.metadata[safe_id]
            
            # Keep only chunks that don't match the document_id
            indices_to_keep = [i for i, meta in enumerate(old_metadata) if meta.get("document_id") != document_id]
            
            if len(indices_to_keep) == len(old_metadata):
                return # Nothing to delete
                
            new_metadata = [old_metadata[i] for i in indices_to_keep]
            
            # Rebuild FAISS index
            new_index = faiss.IndexFlatL2(DIMENSION)
            if new_metadata:
                vectors = []
                for i in indices_to_keep:
                    vec = self.indexes[safe_id].reconstruct(i)
                    vectors.append(vec)
                new_index.add(np.array(vectors).astype('float32'))
                
            self.indexes[safe_id] = new_index
            self.metadata[safe_id] = new_metadata
            self._save_user_index(safe_id)

# Singleton instance
vector_store = VectorStore()
