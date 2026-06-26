from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.agent import main_workflow

router = APIRouter(prefix="/agent", tags=["agent"])


class AgentRequest(BaseModel):
    query: str
    thread_id: str = "default"


class AgentResponse(BaseModel):
    answer: str
    state: dict


@router.post("/invoke", response_model=AgentResponse)
async def invoke_agent(request: AgentRequest):
    try:
        state = await main_workflow.invoke(request.query, thread_id=request.thread_id)
        return AgentResponse(answer=state.get("final_answer", ""), state=state)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
