from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.tools.legacy_adapter import legacy_adapter

router = APIRouter(prefix="/sync", tags=["sync"])


class SyncRequest(BaseModel):
    system_type: str = "api"
    endpoint: str | None = None
    query: str | None = None
    db_url: str | None = None
    directory: str | None = None
    params: dict | None = None


@router.post("/legacy")
async def sync_legacy(request: SyncRequest):
    try:
        kwargs = request.dict(exclude={"system_type"}, exclude_none=True)
        return legacy_adapter.sync_data(system_type=request.system_type, **kwargs)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
