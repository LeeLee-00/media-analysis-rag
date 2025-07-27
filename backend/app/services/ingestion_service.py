import os
import traceback
from pathlib import Path
from datetime import datetime
from app.core.logging.logger import get_logger
from app.core.config import MEDIA_ROOT, WRITE_TO_PG, MIN_SUMMARY_LENGTH, MAX_SUMMARY_LENGTH
from app.core.utils import prepare_image, extract_keyframes, extract_audio
from app.services.analysis_service import extract_image_media_metadata, extract_video_media_metadata
from app.models.media import MediaAnalysis
from app.core.rag_utils import clean_transcript
from app.core.database import es, ELASTIC_INDEX

logger = get_logger(__name__)

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}
VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv"}

def is_duplicate(filename, db):
    in_pg = db.query(MediaAnalysis).filter_by(filename=filename).first()
    in_es = es.exists(index=ELASTIC_INDEX, id=filename)
    return in_pg or in_es

def process_image(path, db, processor, blip_model, summarizer, embed_text):
    try:
        filename = path.name
        if filename.startswith(".") or filename.startswith("._"):
            logger.debug(f"🔕 Skipping hidden/system file: {filename}")
            return
        if is_duplicate(filename, db):
            logger.info(f"⏭️ Skipping already ingested file: {filename}")
            return

        logger.info(f"🖼️ Ingesting image: {filename}")
        image = prepare_image(str(path))
        inputs = processor(image, return_tensors="pt").to(blip_model.device)
        outputs = blip_model.generate(**inputs, max_new_tokens=150)
        caption = processor.decode(outputs[0], skip_special_tokens=True)

        prompt = (
            "This is a description of an image. It includes a visual caption generated from the image. "
            "Summarize the visual content clearly and concisely.\n\n"
            f"Visual: {caption}"
        )
        logger.debug(f"📝 Image Summary Prompt:\n{prompt}")

        summary = summarizer(
            prompt,
            max_length=MAX_SUMMARY_LENGTH,
            min_length=MIN_SUMMARY_LENGTH,
            do_sample=False
        )[0]["summary_text"]

        vector = embed_text(summary)
        metadata = extract_image_media_metadata(str(path))

        es.index(index=ELASTIC_INDEX, id=filename, document={
            "filename": filename,
            "media_type": "image",
            "summary": summary,
            "transcript": "",
            "relative_path": str(path.relative_to(MEDIA_ROOT)),
            "timestamp": datetime.utcnow().isoformat(),
            "vector": vector
        })

        if WRITE_TO_PG:
            media = MediaAnalysis(
                filename=filename,
                media_type="image",
                summary=summary,
                transcript="",
                media_metadata=metadata
            )
            db.add(media)
            db.commit()
        logger.info(f"✅ Ingested image: {filename}")

    except Exception as e:
        logger.error(f"❌ Failed to ingest image {path}: {e}")
        traceback.print_exc()

def process_video(path, db, processor, blip_model, whisper_model, summarizer, embed_text):
    try:
        filename = path.name
        if filename.startswith(".") or filename.startswith("._"):
            logger.debug(f"🔕 Skipping hidden/system file: {filename}")
            return
        if is_duplicate(filename, db):
            logger.info(f"⏭️ Skipping already ingested file: {filename}")
            return

        logger.info(f"🎥 Ingesting video: {filename}")
        video_path = str(path)
        metadata = extract_video_media_metadata(video_path)

        frame_paths = extract_keyframes(video_path, max_frames=15)
        captions = []
        for frame_path in frame_paths:
            image = prepare_image(frame_path)
            inputs = processor(image, return_tensors="pt").to(blip_model.device)
            outputs = blip_model.generate(**inputs, max_new_tokens=30)
            captions.append(processor.decode(outputs[0], skip_special_tokens=True))
        combined_visual = " ".join(captions)

        audio_path = video_path.rsplit(".", 1)[0] + ".wav"
        extract_audio(video_path, audio_path)

        try:
            raw_transcript = whisper_model.transcribe(audio_path).get("text", "")
            logger.debug(f"Raw transcript output: {raw_transcript}")
            cleaned_transcript = clean_transcript(raw_transcript)
            logger.debug(f"Cleaned transcript output: {cleaned_transcript}")
        except Exception as e:
            logger.warning(f"🔇 Transcription failed: {e}")
            cleaned_transcript = ""

        multimodal_content = f"Visual: {combined_visual}\nAudio: {cleaned_transcript}"
        prompt = (
            "This is a description of a video. It includes a visual description followed by a transcript. "
            "Summarize it concisely.\n\n"
            f"{multimodal_content}"
        )
        logger.debug(f"📝 Summary Prompt:\n{prompt}")

        summary = summarizer(
            prompt,
            max_length=MAX_SUMMARY_LENGTH,
            min_length=MIN_SUMMARY_LENGTH,
            do_sample=False
        )[0]["summary_text"]

        vector = embed_text(summary)

        es.index(index=ELASTIC_INDEX, id=filename, document={
            "filename": filename,
            "media_type": "video",
            "summary": summary,
            "transcript": cleaned_transcript,
            "media_metadata": metadata,
            "relative_path": str(path.relative_to(MEDIA_ROOT)),
            "timestamp": datetime.utcnow().isoformat(),
            "vector": vector
        })

        if WRITE_TO_PG:
            media = MediaAnalysis(
                filename=filename,
                media_type="video",
                summary=summary,
                transcript=cleaned_transcript,
                media_metadata=metadata
            )
            db.add(media)
            db.commit()

        logger.info(f"✅ Ingested video: {filename}")

        for frame_path in frame_paths:
            os.remove(frame_path)
        if os.path.exists(audio_path):
            os.remove(audio_path)

    except Exception as e:
        logger.error(f"❌ Failed to ingest video {path}: {e}")
        traceback.print_exc()
