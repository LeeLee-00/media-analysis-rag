import os
import mimetypes
import asyncio
from io import BytesIO
from starlette.datastructures import UploadFile

from app.services.analysis_service import analyze_video
from app.services.storage_service import store_analysis_result
from app.core.database import AsyncSessionLocal
from app.core.logging.logger import get_logger

logger = get_logger(__name__)

# Only process the videos directory
VIDEO_DIR = "/easystore/DC_25_Data/videos"
OVERWRITE = True  # Set to False if you want to skip existing records

def get_content_type(path: str) -> str:
    mime, _ = mimetypes.guess_type(path)
    return mime or "application/octet-stream"

def create_upload_file(path: str) -> UploadFile:
    with open(path, "rb") as f:
        content = f.read()
    return UploadFile(
        filename=os.path.basename(path),
        file=BytesIO(content)
    )

async def process_file(path: str):
    logger.info(f"📂 Processing file: {path}")
    content_type = get_content_type(path)
    media_type = content_type.split("/")[0]

    if media_type != "video":
        logger.warning(f"🚫 Skipping non-video file: {path}")
        return

    upload = create_upload_file(path)

    try:
        async with AsyncSessionLocal() as db:
            result = await analyze_video(upload)

            await store_analysis_result(
                db=db,
                filename=result["filename"],
                media_type=result["media_type"],
                summary=result["summary"],
                transcript=result.get("transcript", ""),
                metadata=result["media_metadata"],
                vector=result.get("vector"),
                overwrite=OVERWRITE
            )

    except Exception as e:
        logger.error(f"❌ Failed to process {path}: {e}")

async def batch_ingest():
    logger.info("🚀 Starting recursive video-only batch ingestion...")

    files = []
    for root, _, filenames in os.walk(VIDEO_DIR):
        for filename in filenames:
            full_path = os.path.join(root, filename)
            if os.path.isfile(full_path):
                files.append(full_path)

    logger.info(f"🔍 Found {len(files)} video file(s) to process.")

    for file_path in files:
        await process_file(file_path)

    logger.info("✅ Recursive video ingestion complete.")

if __name__ == "__main__":
    asyncio.run(batch_ingest())
