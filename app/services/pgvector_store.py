from typing import List, Optional
import numpy as np

class PgVectorStore:
    def __init__(self, supabase_client):
        self.client = supabase_client

    def add_chunks(self, chunks: List, embeddings: np.ndarray, user_id: str, file_id: Optional[str], filename: Optional[str]):
        rows = [
            {
                "user_id": user_id,
                "file_id": file_id,
                "filename": filename,
                "content": chunk.page_content,
                "embedding": emb.tolist(),
            }
            for chunk, emb in zip(chunks, embeddings)
        ]
        self.client.table("document_chunks").insert(rows).execute()

    def query(self, query_embedding: np.ndarray, top_k: int = 5):
        embedding_list = query_embedding[0].tolist() if query_embedding.ndim == 2 else query_embedding.tolist()
        result = self.client.rpc(
            "match_document_chunks",
            {"query_embedding": embedding_list, "match_count": top_k},
        ).execute()
        return result.data