from src.data_loader import load_all_documents
from src.vectorstore import FaissVectorStore
from src.search import RAGSearch
from src.embedding import EmbeddingPipeline

# Example usage
if __name__ == "__main__":

    store = FaissVectorStore();
    store.load()
    print(store.query("What is agentic RAG?", top_k=3))
    rag_search = RAGSearch()
    query = "What is agentic RAG?"
    summary = rag_search.search_and_summarize(query, top_k=3)
    print("Summary:", summary)