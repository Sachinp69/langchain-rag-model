from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.core.auth import get_current_user, get_current_token
from app.core.supabase_client import get_user_supabase_client

router = APIRouter()

# @router.post("/upload")
# async def upload_file(
#     file: UploadFile = File(...),
#     user_id: str = Depends(get_current_user),
#     token: str = Depends(get_current_token),
# ):
#     supabase = get_user_supabase_client(token)
#     content = await file.read()
#     storage_path = f"{user_id}/{file.filename}"

#     try:
#         supabase.storage.from_("userfiles").upload(
#             storage_path, content
#         )
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))

#     supabase.table("files").insert({
#         "user_id": user_id,
#         "filename": file.filename,
#         "storage_path": storage_path,
#     }).execute()

#     return {"filename": file.filename, "storage_path": storage_path}
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user),
    token: str = Depends(get_current_token),
):
    supabase = get_user_supabase_client(token)
    content = await file.read()
    storage_path = f"{user_id}/{file.filename}"

    try:
        result = supabase.storage.from_("userfiles").upload(
            storage_path, content
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"storage: {str(e)}")

    try:
        insert_result = supabase.table("files").insert({
            "user_id": user_id,
            "filename": file.filename,
            "storage_path": storage_path,
        }).execute()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"table: {str(e)}")

    return {"filename": file.filename, "storage_path": storage_path}