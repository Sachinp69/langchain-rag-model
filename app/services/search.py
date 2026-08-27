import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from sentence_transformers import SentenceTransformer
from app.services.pgvector_store import PgVectorStore

load_dotenv()

class RAGSearch:
    def __init__(self, supabase_client, embedding_model: str = "all-MiniLM-L6-v2", llm_model: str = "openai/gpt-oss-20b"):
        self.model = SentenceTransformer(embedding_model)
        self.store = PgVectorStore(supabase_client)
        self.llm = ChatGroq(model=llm_model)
        print(f"[INFO] Groq LLM initialized: {llm_model}")

    def search_and_summarize(self, query: str, top_k: int = 5) -> str:
        query_emb = self.model.encode([query]).astype('float32')
        results = self.store.query(query_emb, top_k=top_k)

        texts = [r["content"] for r in results if r.get("content")]
        context = "\n\n".join(texts)

        if not context:
            return "No relevant documents found for your query."

        prompt = f"""Summarize the following context for the query: '{query}'\n\nContext:\n{context}\n\nSummary:"""
        response = self.llm.invoke([prompt])

        if isinstance(response.content, str):
            return response.content
        elif isinstance(response.content, list):
            return "".join(
                part if isinstance(part, str) else part.get("text", "")
                for part in response.content
            )
        return str(response.content)