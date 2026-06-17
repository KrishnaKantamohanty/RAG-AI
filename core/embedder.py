from sentence_transformers import SentenceTransformer
import numpy as np

# Cache the model loading at module level
_MODEL_CACHE = None

def load_model():
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        _MODEL_CACHE = SentenceTransformer("all-MiniLM-L6-v2")
    return _MODEL_CACHE

class Embedder:
    """
    Embedder converts text into dense vector embeddings using sentence-transformers.
    """
    def __init__(self):
        self.model = load_model()
        
    def embed(self, texts: list[str]) -> np.ndarray:
        """
        Embeds a list of texts and returns normalized embeddings.
        """
        if not texts:
            return np.empty((0, 384))
            
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        # Normalize to unit vectors for inner product (cosine similarity)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1 # Avoid division by zero
        normalized_embeddings = embeddings / norms
        return normalized_embeddings
        
    def embed_query(self, query: str) -> np.ndarray:
        """
        Embeds a single query string.
        """
        embedding = self.model.encode([query], convert_to_numpy=True)
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm == 0:
            norm = 1
        return embedding / norm
