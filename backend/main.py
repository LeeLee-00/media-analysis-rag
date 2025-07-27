# main.py
from fastapi import FastAPI
from app.api.endpoints import search_media, health, upload_media, rag
from app.core.database import init_db
from app.core.elasticsearch import init_elasticsearch
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run on startup
    await init_db()
    await init_elasticsearch()
    yield

app = FastAPI(
    title="Media Analysis API",
    description="AI-powered multimodal analysis for image/video",
    version="1.0.0",
    lifespan=lifespan
)

# Register routers
app.include_router(rag.router, prefix="/rag", tags=["RAG Search"])
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(upload_media.router, prefix="/upload", tags=["Media Upload"])
app.include_router(search_media.router, prefix="/search", tags=["Keyword Search"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Media Analysis API. Use /docs to explore endpoints."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
