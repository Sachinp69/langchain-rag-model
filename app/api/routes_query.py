from fastapi import APIRouter, Depends, HTTPException
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
    request: QueryRequest,
    user_id: str = Depends(get_current_user),
    token: str = Depends(get_current_token),
):
    supabase = get_user_supabase_client(token)

    try:
        rag = RAGSearch(supabase)
        answer = rag.search_and_summarize(request.query, top_k=request.top_k)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"query: {str(e)}")

    return {"query": request.query, "answer": answer}