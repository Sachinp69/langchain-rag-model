from fastapi import FastAPI, Depends
from app.core.auth import get_current_user

app = FastAPI(title="BrainDrop")

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/me")
def read_current_user(user_id: str = Depends(get_current_user)):
    return {"user_id": user_id}
