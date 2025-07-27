from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import Optional
import os
import tempfile
from app.services.analysis_service import analyze_image
from app.services.storage_service import store_analysis_result
from app.api.response import AnalysisResult
from app.core.database import get_db
from app.core.logging.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.post("/image", response_model=AnalysisResult)
async def analyze_image_endpoint(
    file: UploadFile = File(...),
    overwrite: Optional[bool] = Query(True, description="Overwrite existing entry if it exists"),
    db: Session = Depends(get_db)
):
    logger.info(f"📥 Received image upload: {file.filename} ({file.content_type})")

    if not file.content_type.startswith("image/"):
        logger.warning(f"⛔ Rejected non-image file: {file.filename}")
        raise HTTPException(status_code=400, detail="File must be an image")

    temp_path = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp:
            temp.write(await file.read())
            temp_path = temp.name
        logger.debug(f"📁 Temp file created at: {temp_path}")

        await file.seek(0)
        result = await analyze_image(file)

        store_analysis_result(
            db=db,
            filename=result["filename"],
            media_type="image",
            summary=result["summary"],
            transcript=result["transcript"],
            metadata=result["media_metadata"],
            vector=result.get("vector"),
            overwrite=overwrite
        )

        return result

    except Exception as e:
        logger.exception(f"❌ Failed to process image {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)
            logger.debug(f"🗑 Deleted temp file: {temp_path}")
