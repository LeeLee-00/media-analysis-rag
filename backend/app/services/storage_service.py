from app.core.elasticsearch import es
from app.core.config import ELASTIC_INDEX
from app.core.logging.logger import get_logger
from app.models.media import MediaAnalysis
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)

async def store_analysis_result(
    db: AsyncSession,  
    filename: str,
    media_type: str,
    summary: str,
    transcript: str,
    metadata: dict,
    vector: list = None,
    overwrite: bool = True
):
    try:
        result = await db.execute(
            select(MediaAnalysis).filter_by(filename=filename, media_type=media_type)
        )
        existing = result.scalar_one_or_none()

        if existing:
            if overwrite:
                logger.info(f"📝 Overwriting existing record in PostgreSQL for: {filename}")
                await db.delete(existing)
                await db.commit()
            else:
                logger.info(f"⏭️ Skipping PostgreSQL insert (exists + no overwrite): {filename}")
                return

        media = MediaAnalysis(
            filename=filename,
            media_type=media_type,
            summary=summary,
            transcript=transcript,
            media_metadata=metadata
        )
        db.add(media)
        await db.commit()
        logger.info(f"✅ Stored metadata in PostgreSQL: {filename}")
    except Exception as e:
        logger.error(f"❌ Failed to store analysis result for {filename}: {e}")
        raise

    es_doc = {
        "filename": filename,
        "media_type": media_type,
        "summary": summary,
        "transcript": transcript,
        "media_metadata": metadata,
        "timestamp": datetime.utcnow().isoformat()
    }
    if vector is not None:
        es_doc["vector"] = vector

    es.index(index=ELASTIC_INDEX, id=filename, document=es_doc)
    logger.info(f"📦 Indexed in Elasticsearch: {filename}")

