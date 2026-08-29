from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request
from app.core.auth import get_current_user, get_current_token
from app.core.supabase_client import get_user_supabase_client
from app.services.ingestion import ingest_file
from typing import cast, Any, Dict

router = APIRouter()

@router.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user),
    token: str = Depends(get_current_token),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="File must have a filename")
    supabase = get_user_supabase_client(token)
    content = await file.read()
    storage_path = f"{user_id}/{file.filename}"

    try:
        supabase.storage.from_("userfiles").upload(storage_path, content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"storage: {str(e)}")

    try:
        insert_result = supabase.table("files").insert({
            "user_id": user_id,
            "filename": file.filename,
            "storage_path": storage_path,
        }).execute()
        data = insert_result.data
        assert data and len(data) > 0
        row = cast(Dict[str, Any], data[0])
        file_id: str = str(row["id"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"table: {str(e)}")

    try:
        ingest_file(content, file.filename, user_id, file_id, supabase, request.app.state.embedding_model)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"ingestion: {str(e)}")

    return {"filename": file.filename, "storage_path": storage_path}
