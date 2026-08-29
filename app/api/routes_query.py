from fastapi import APIRouter, Depends, HTTPException, Request

from pydantic import BaseModel
from app.core.auth import get_current_user, get_current_token
from app.core.supabase_client import get_user_supabase_client
from app.services.search import RAGSearch

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

@router.post("/query")
async def query_documents(
    request_body: QueryRequest,
    request: Request,
    user_id: str = Depends(get_current_user),
    token: str = Depends(get_current_token),
):
    supabase = get_user_supabase_client(token)
    rag = RAGSearch(supabase, request.app.state.embedding_model, request.app.state.llm)

    try:
        answer = rag.search_and_summarize(request_body.query, top_k=request_body.top_k)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"query: {str(e)}")

    return {"query": request_body.query, "answer": answer}