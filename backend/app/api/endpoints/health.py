# app/api/endpoints/health.py
from fastapi import APIRouter
from app.core.logging.logger import get_logger

logger = get_logger(__name__)


router = APIRouter()

@router.get("/health", tags=["Health"])
async def health_check():
    logger.info("Health check endpoint called.")
    return {"status": "ok"}
