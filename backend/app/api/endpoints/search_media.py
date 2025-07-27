from fastapi import Depends, APIRouter, HTTPException
from app.core.database import get_db 
from app.core.elasticsearch import es
from sqlalchemy.orm import Session
from app.core.logging.logger import get_logger
from app.core.config import ELASTIC_INDEX

logger = get_logger(__name__)


router = APIRouter()

@router.get("/media")
def search_media(query: str, db: Session = Depends(get_db)):
    logger.info(f"Search query received: '{query}'")

    search_body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["summary", "transcript"],
                "fuzziness": "AUTO",
                "operator": "and"
            }
        }
    }

    try:
        res = es.search(index=ELASTIC_INDEX, body=search_body)
        logger.info(f"Search completed: {len(res['hits']['hits'])} results found for '{query}'")
    except Exception as exc:
        logger.error(f"Elasticsearch search failed: {exc}")
        raise HTTPException(status_code=500, detail="Search failed.")

    results = [
        {
            "filename": hit["_source"].get("filename", ""),
            "summary": hit["_source"].get("summary", ""),
            "media_type": hit["_source"].get("media_type", ""),
            "transcript": hit["_source"].get("transcript", ""), 
            "media_metadata": hit["_source"].get("media_metadata", {}) 
        }
        for hit in res["hits"]["hits"]
    ]


    return {"results": results}

