import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from app.services.vectorstore import FaissVectorStore
from app.services.data_loader import load_all_documents

load_dotenv()

class RAGSearch:
    def __init__(self, persist_dir: str = "faiss_store", embedding_model: str = "all-MiniLM-L6-v2", llm_model: str = "openai/gpt-oss-20b"):
        self.persist_dir = persist_dir
        self.vectorstore = FaissVectorStore(persist_dir, embedding_model)

        faiss_path = os.path.join(persist_dir, "faiss.index")
        meta_path = os.path.join(persist_dir, "metadata.pkl")
        manifest_path = os.path.join(persist_dir, "manifest.json")

        current_files = sorted(f for f in os.listdir("data") if f.lower().endswith(".pdf"))

        indexed_files = []
        if os.path.exists(manifest_path):
            with open(manifest_path, "r") as f:
                indexed_files = json.load(f)

        index_exists = os.path.exists(faiss_path) and os.path.exists(meta_path)
        needs_rebuild = (not index_exists) or (current_files != indexed_files)

        if needs_rebuild:
            print(f"[INFO] Rebuilding index. Current PDFs: {current_files} | Previously indexed: {indexed_files}")
            self.vectorstore.index = None
            self.vectorstore.metadata = []
            docs = load_all_documents("data")
            self.vectorstore.build_from_documents(docs)
            with open(manifest_path, "w") as f:
                json.dump(current_files, f)
        else:
            self.vectorstore.load()

        groq_api_key = os.getenv("GROQ_API_KEY")
        self.llm = ChatGroq(model=llm_model)
        print(f"[INFO] Groq LLM initialized: {llm_model}")

    def search_and_summarize(self, query: str, top_k: int = 5) -> str:

        results = self.vectorstore.query(query, top_k=top_k)
        texts = [r["metadata"].get("text", "") for r in results if r["metadata"]]
        context = "\n\n".join(texts)

        if not context:
            return "No relevant documents found."

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
