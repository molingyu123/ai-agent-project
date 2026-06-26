from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from knowledge_base.indexer import KnowledgeIndexer

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


class IndexTextRequest(BaseModel):
    text: str = Field(min_length=1)
    source: str
    title: str | None = None
    metadata: dict = Field(default_factory=dict)


@router.post("/index-text")
async def index_text(request: IndexTextRequest):
    try:
        indexer = KnowledgeIndexer()
        return indexer.index_text(
            text=request.text,
            source=request.source,
            title=request.title,
            metadata=request.metadata,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
