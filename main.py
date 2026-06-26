from fastapi import FastAPI

from api.routes import agent_router, chat_router, knowledge_router, sync_router
from core.database import init_db

app = FastAPI(title="AI Agent Project")


@app.on_event("startup")
async def startup():
    init_db()


@app.get("/")
async def root():
    return {"message": "AI Agent Production Ready!"}

@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(chat_router)
app.include_router(agent_router)
app.include_router(knowledge_router)
app.include_router(sync_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
