from fastapi import FastAPI
from api.routes import chat_router

app = FastAPI(title="AI Agent Project")

@app.get("/")
async def root():
    return {"message": "AI Agent Production Ready!"}

# Include routes
app.include_router(chat_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
