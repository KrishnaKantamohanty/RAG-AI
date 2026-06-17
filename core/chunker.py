from langchain_text_splitters import RecursiveCharacterTextSplitter

class TextChunker:
    """
    TextChunker splits large text into smaller chunks for embeddings.
    """
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=600,
            chunk_overlap=100
        )
        
    def chunk(self, text: str) -> list[str]:
        """
        Splits text into chunks, filtering out small chunks and adding metadata.
        """
        chunks = self.splitter.split_text(text)
        
        valid_chunks = []
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) >= 30:
                # Adding metadata indicating chunk index
                chunk_with_meta = f"[Chunk {i+1}] {chunk}"
                valid_chunks.append(chunk_with_meta)
                
        return valid_chunks
