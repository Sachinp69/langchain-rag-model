from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from sentence_transformers import SentenceTransformer
from langchain_groq import ChatGroq
from app.core.auth import get_current_user
from app.api.routes_upload import router as upload_router
from app.api.routes_query import router as query_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[INFO] Loading embedding model + LLM at startup...")
    app.state.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    app.state.llm = ChatGroq(model="openai/gpt-oss-20b")
    print("[INFO] Models loaded.")
    yield

app = FastAPI(title="BrainDrop", lifespan=lifespan)

app.include_router(upload_router)
app.include_router(query_router)

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/me")
def read_current_user(user_id: str = Depends(get_current_user)):
    return {"user_id": user_id}
