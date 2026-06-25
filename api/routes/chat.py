"""
FastAPI routes for Chat / Knowledge Q&A.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from knowledge_base.retriever import retriever
# from langchain_openai import ChatOpenAI  # Uncomment when LLM ready
import logging

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    question: str
    # session_id: str = None  # For memory later

class ChatResponse(BaseModel):
    answer: str
    sources: list = []

@router.post("/query")
async def knowledge_query(request: ChatRequest):
    """Knowledge Q&A endpoint with RAG"""
    try:
        # llm = ChatOpenAI(...)  # Integrate later
        result = retriever.query(request.question)
        return ChatResponse(
            answer=result.get("answer", "I don't have enough information."),
            sources=result.get("sources", [])
        )
    except Exception as e:
        logger.error(f"Chat query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health():
    return {"status": "Chat service ready"}