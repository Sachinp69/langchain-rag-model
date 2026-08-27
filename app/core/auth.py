from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import httpx
from app.core.config import settings

security = HTTPBearer()

JWKS_URL = f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"
_jwks_cache = None

def get_jwks():
    global _jwks_cache
    if _jwks_cache is None:
        resp = httpx.get(JWKS_URL)
        _jwks_cache = resp.json()
    return _jwks_cache

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    payload = _decode(credentials.credentials)
    sub = payload.get("sub")
    if not isinstance(sub, str):
        raise HTTPException(status_code=401, detail="Invalid token: no user id")
    return sub

def get_current_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    _decode(credentials.credentials)  
    return credentials.credentials

def _decode(token: str) -> dict:
    try:
        jwks = get_jwks()
        return jwt.decode(token, jwks, algorithms=["ES256"], audience="authenticated")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")