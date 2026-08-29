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

@router.get("/files")
async def list_files(
    user_id: str = Depends(get_current_user),
    token: str = Depends(get_current_token),
):
    supabase = get_user_supabase_client(token)
    result = supabase.table("files").select("id, filename, storage_path, created_at").execute()
    return {"files": result.data}


@router.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    # only need user_id variable for auth validation return value not used
    user_id: str = Depends(get_current_user),
    token: str = Depends(get_current_token),
):
    supabase = get_user_supabase_client(token)

    # fetch the file row first, to get its storage_path
    result = supabase.table("files").select("storage_path").eq("id", file_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="File not found")

    row = cast(Dict[str, Any], result.data[0])
    storage_path = row["storage_path"]
    # delete from storage
    try:
        supabase.storage.from_("userfiles").remove([storage_path])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"storage delete: {str(e)}")

    # delete from files table (document_chunks cascade-deletes via file_id FK)
    try:
        supabase.table("files").delete().eq("id", file_id).execute()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"table delete: {str(e)}")

    return {"deleted": file_id}
