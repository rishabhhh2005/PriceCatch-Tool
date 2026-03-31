from fastapi import APIRouter, Depends
from backend.auth import require_api_key
from backend.services.ingest import ingest_all

refresh_router = APIRouter()

@refresh_router.post("/refresh", dependencies=[Depends(require_api_key)])
async def trigger_refresh():
    """Trigger data refresh."""
    results = await ingest_all()
    return results
