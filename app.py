from app.services.data_loader import load_all_documents
from app.services.vectorstore import FaissVectorStore
from app.services.search import RAGSearch
from app.services.embedding import EmbeddingPipeline

# Example usage
if __name__ == "__main__":

    store = FaissVectorStore();
    store.load()
    print(store.query("What is agentic RAG?", top_k=3))
    rag_search = RAGSearch()
    query = "What is agentic RAG?"
    summary = rag_search.search_and_summarize(query, top_k=3)
    print("Summary:", summary)
