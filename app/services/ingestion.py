import numpy as np
from app.services.data_loader import load_single_document
from app.services.embedding import EmbeddingPipeline
from app.services.pgvector_store import PgVectorStore
from sentence_transformers import SentenceTransformer


def ingest_file(
    content: bytes,
    filename: str,
    user_id: str,
    file_id: str,
    supabase_client,
    embedding_model : SentenceTransformer,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
):
    docs = load_single_document(filename, content)

    emb_pipe = EmbeddingPipeline(model_name=embedding_model, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = emb_pipe.chunk_documents(docs)
    embeddings = np.array(emb_pipe.embed_chunks(chunks)).astype('float32')

    store = PgVectorStore(supabase_client)
    store.add_chunks(chunks, embeddings, user_id=user_id, file_id=file_id, filename=filename)
