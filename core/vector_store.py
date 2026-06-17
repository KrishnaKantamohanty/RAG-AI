import faiss
import numpy as np

class VectorStore:
    """
    VectorStore holds the FAISS index and the corresponding chunks of text.
    """
    def __init__(self):
        self.chunks = []
        self.index = None
        
    def add(self, chunks: list[str], embeddings: np.ndarray):
        """
        Adds text chunks and their embeddings to the vector store.
        """
        if len(chunks) == 0:
            return
            
        dimension = embeddings.shape[1]
        
        # Initialize index if it doesn't exist
        if self.index is None:
            # Using IndexFlatIP for cosine similarity since vectors are normalized
            self.index = faiss.IndexFlatIP(dimension)
            
        self.index.add(embeddings)
        self.chunks.extend(chunks)
        
    def search(self, query_embedding: np.ndarray, top_k=5) -> tuple[list[str], list[float]]:
        """
        Searches the index for the most relevant chunks.
        Returns a tuple of (results, scores).
        """
        if self.is_empty():
            return [], []
            
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        scores = []
        for i, idx in enumerate(indices[0]):
            if idx != -1 and idx < len(self.chunks):
                results.append(self.chunks[idx])
                scores.append(float(distances[0][i]))
                
        return results, scores
        
    def is_empty(self) -> bool:
        """
        Returns True if the vector store is empty.
        """
        return self.index is None or self.index.ntotal == 0
