# app/services/analysis_service.py
import os
import shutil
from typing import Optional
from fastapi import UploadFile
from app.core.utils import (
    extract_image_media_metadata,
    extract_video_media_metadata,
    extract_audio,
    extract_keyframes,
)
from app.core.config import TEMP_DIR, CLEANUP_TEMP_FILES, MAX_FRAME_COUNT
from app.core.logging.logger import get_logger
from app.core.ai_models import get_model_loader
from app.core.prompt_templates import image_prompt, video_prompt
import time

logger = get_logger(__name__)
model_loader = get_model_loader()

async def analyze_image(file: UploadFile, include_debug: bool = False):
    logger.info(f"🖼️ Starting image analysis for: {file.filename}")
    image_path = os.path.join(TEMP_DIR, file.filename)

    
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    media_metadata = extract_image_media_metadata(image_path)

    # Ollama Vision Model inference
    vision_description = model_loader.vision_infer(
        image_path=image_path,
        prompt=image_prompt("Describe this image and extract key details.")
    )

    summary = model_loader.summarize_text(
        text=vision_description,
        prompt="Summarize the content of this image in a clear and concise paragraph."
    )

    vector = model_loader.embed_query(summary)

    if CLEANUP_TEMP_FILES and os.path.exists(image_path):
        os.remove(image_path)
        logger.debug(f"🧹 Deleted temp image file: {image_path}")

    result = {
        "filename": file.filename,
        "media_type": "image",
        "summary": summary,
        "transcript": "",
        "media_metadata": media_metadata,
        "vector": vector,
    }

    if include_debug:
        result.update({
            "ollama_raw": vision_description
        })

    return result

async def analyze_video(file: UploadFile, include_debug: bool = True):
    logger.info(f"🎥 Starting video analysis for: {file.filename}")
    video_path = os.path.join(TEMP_DIR, file.filename)

    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    media_metadata = extract_video_media_metadata(video_path)

    # Step 1: Extract keyframes
    logger.info("🎞️ Extracting keyframes...")
    frame_paths = extract_keyframes(video_path, max_frames=MAX_FRAME_COUNT)
    logger.info(f"🖼️ {len(frame_paths)} frame(s) extracted.")

    # Step 2: Run Ollama Vision on frames
    captions = []
    for i, frame_path in enumerate(frame_paths):
        logger.info(f"🔍 Analyzing frame {i + 1}/{len(frame_paths)}: {os.path.basename(frame_path)}")
        try:
            vision_description = model_loader.vision_infer(
                image_path=frame_path,
                prompt=image_prompt("Describe this video frame.")
            )
            captions.append(vision_description)
        except Exception as e:
            logger.error(f"❌ Ollama vision failed on frame {frame_path}: {e}")
            captions.append("[Failed to analyze frame]")

    combined_visual = " ".join(captions)
    frame_info = [{"frame_number": i+1, "caption": cap} for i, cap in enumerate(captions)]

    # Start timer for video analysis
    start = time.perf_counter()
    logger.debug(f"⏱️ Total video analysis time: {time.perf_counter() - start:.2f} seconds")
    
    # Step 3: Extract and transcribe audio
    logger.info("🔊 Extracting audio...")
    audio_path = video_path.rsplit(".", 1)[0] + ".wav"
    extract_audio(video_path, audio_path)

    transcript = ""
    try:
        logger.info("🗣️ Transcribing audio with Whisper...")
        result = model_loader.transcribe_audio(audio_path)
        transcript = result.strip()
        logger.info("📝 Transcription complete.")
    except Exception as e:
        logger.warning(f"🔇 Whisper transcription failed for {file.filename}: {e}")

    # Step 4: Summarization and embedding
    logger.info("🧠 Running final summarization...")
    prompt = video_prompt(combined_visual, transcript)
    summary = model_loader.summarize_text(text=prompt, prompt="Summarize the video content clearly.")
    logger.info("📄 Summary generated.")

    logger.info("📌 Creating vector embedding...")
    vector = model_loader.embed_query(summary)

    # Step 5: Build payload
    result_payload = {
        "filename": file.filename,
        "media_type": "video",
        "summary": summary,
        "transcript": transcript,
        "media_metadata": media_metadata,
        "vector": vector,
        "frames": frame_info,
        "frame_count": len(frame_paths)
    }

    if include_debug:
        logger.debug(f"Combined Visual Captions: {combined_visual}")
        result_payload.update({
            "combined_visual": combined_visual,
            "ollama_video_prompt": prompt
        })

    # Step 6: Cleanup temporary files
    if CLEANUP_TEMP_FILES:
        logger.info("🧹 Cleaning up temp files...")
        for path in [video_path, audio_path, *frame_paths]:
            if os.path.exists(path):
                os.remove(path)

    logger.info("✅ Video analysis complete.")
    return result_payload
