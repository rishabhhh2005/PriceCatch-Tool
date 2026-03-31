import hashlib
import secrets
from fastapi import HTTPException, Header, Depends, Request
from sqlalchemy.orm import Session
from backend.database import get_session
from backend.models import ApiKey, ApiUsage
from fastapi import APIRouter
from pydantic import BaseModel

auth_router = APIRouter()

def hash_key(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()

class KeyCreateRequest(BaseModel):
    name: str

class KeyCreateResponse(BaseModel):
    name: str
    key: str

def seed_default_api_key():
    from backend.database import SessionLocal
    db = SessionLocal()
    default_key = "dev-key-12345"
    key_hash = hash_key(default_key)
    
    if not db.query(ApiKey).filter(ApiKey.key_hash == key_hash).first():
        db.add(ApiKey(key_hash=key_hash, name="Default Dev Key"))
        db.commit()
    db.close()

async def require_api_key(
    request: Request,
    x_api_key: str = Header(None),
    session: Session = Depends(get_session)
):
    if not x_api_key:
        raise HTTPException(status_code=401, detail="Missing API key")
        
    key_hash = hash_key(x_api_key)
    api_key_record = session.query(ApiKey).filter(
        ApiKey.key_hash == key_hash,
        ApiKey.is_active == True
    ).first()

    if not api_key_record:
        raise HTTPException(status_code=401, detail="Invalid or inactive API key")

    usage = ApiUsage(
        key_hash=key_hash,
        endpoint=str(request.url.path)
    )
    session.add(usage)
    session.commit()

    return api_key_record

@auth_router.post("/auth/keys", response_model=KeyCreateResponse, dependencies=[Depends(require_api_key)])
async def create_api_key(req: KeyCreateRequest, session: Session = Depends(get_session)):
    new_raw_key = f"key_{secrets.token_urlsafe(16)}"
    key_hash = hash_key(new_raw_key)
    
    api_key = ApiKey(key_hash=key_hash, name=req.name)
    session.add(api_key)
    session.commit()
    
    return {"name": req.name, "key": new_raw_key}
