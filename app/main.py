from fastapi import FastAPI, Depends
from app.core.auth import get_current_user
from app.api.routes_upload import router as upload_router
from app.api.routes_query import router as query_router

app = FastAPI(title="BrainDrop")

app.include_router(upload_router)
app.include_router(query_router)

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/me")
def read_current_user(user_id: str = Depends(get_current_user)):
    return {"user_id": user_id}
