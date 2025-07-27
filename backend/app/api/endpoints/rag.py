# app/api/endpoints/rag_search.py

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.services.rag_search import RAGQuery, run_rag_pipeline
from app.core.logging.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/custom", response_model=Dict[str, Any])
def custom_rag_search(params: RAGQuery) -> Dict[str, Any]:
    try:
        return run_rag_pipeline(
            query=params.query,
            top_k=params.top_k,
            score_threshold=params.score_threshold,
            fallback_to_keyword=params.fallback_to_keyword,
            debug=params.debug
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
