import os
import cv2
from PIL import Image
import numpy as np
from app.core.config import TEMP_DIR
from moviepy.editor import VideoFileClip
from app.core.logging.logger import get_logger
from pathlib import Path
from PIL.ExifTags import TAGS
import os

import datetime
from pathlib import Path

logger = get_logger(__name__)

def prepare_image(image_path):
    """
    Load and prepare an image for processing with the image captioning model.
    
    Args:
        image_path (str): Path to the image file
        
    Returns:
        PIL.Image: Processed image ready for model input
    """
    try:
        # Open image with PIL
        image = Image.open(image_path).convert('RGB')
        return image
    except Exception as e:
        logger.warning(f"Failed to load image {image_path}: {e}")
        # Return a simple colored image as fallback
        return Image.new('RGB', (224, 224), color='gray')


def extract_audio(video_path: str, audio_output_path: str) -> str:
    try:
        clip = VideoFileClip(video_path)
        clip.audio.write_audiofile(audio_output_path, logger=None)
        return audio_output_path
    except Exception as e:
        logger.warning(f"Audio extraction failed: {video_path}: {e}")
        return ""


def extract_keyframes(video_path, max_frames=5):
    """
    Extract key frames from a video.
    
    Args:
        video_path (str): Path to the video file
        max_frames (int): Maximum number of frames to extract
        
    Returns:
        list: List of paths to extracted frames
    """
    try:
        # Open the video file
        video = cv2.VideoCapture(video_path)
        
        # Get video properties
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = video.get(cv2.CAP_PROP_FPS)
        duration = total_frames / fps if fps > 0 else 0
        
        # Calculate intervals to extract frames evenly
        if total_frames <= max_frames or total_frames <= 0:
            # If video is shorter than max_frames, take all frames
            frame_indices = list(range(total_frames))
        else:
            # Otherwise, take evenly spaced frames
            interval = total_frames / max_frames
            frame_indices = [int(i * interval) for i in range(max_frames)]
        
        frame_paths = []
        for idx in frame_indices:
            # Set the video position
            video.set(cv2.CAP_PROP_POS_FRAMES, idx)
            success, frame = video.read()
            
            if success:
                # Save the frame
                frame_path = os.path.join(TEMP_DIR, f"frame_{idx}.jpg")
                cv2.imwrite(frame_path, frame)
                frame_paths.append(frame_path)
        
        video.release()
        return frame_paths
    
    except Exception as e:
        print(f"Error extracting keyframes: {e}")
        return []

def extract_video_media_metadata(video_path):
    media_metadata = {
        "filename": os.path.basename(video_path),
        "file_size": os.path.getsize(video_path),
        "file_type": Path(video_path).suffix[1:],
        "last_modified": datetime.datetime.fromtimestamp(os.path.getmtime(video_path)).isoformat(),
    }

    try:
        video = cv2.VideoCapture(video_path)
        if video.isOpened():
            fps = video.get(cv2.CAP_PROP_FPS)
            frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0

            media_metadata["fps"] = round(fps, 2)
            media_metadata["frame_count"] = frame_count
            media_metadata["dimensions"] = f"{width}x{height}"
            media_metadata["duration"] = f"{int(duration // 60)}:{int(duration % 60):02d}"
            media_metadata["duration_seconds"] = round(duration, 2)

            video.release()
    except Exception as e:
        logger.warning(f"Video metadata extraction failed for {video_path}: {e}")
        media_metadata["video_error"] = str(e)

    return media_metadata


def extract_image_media_metadata(image_path):
    media_metadata = {
        "filename": os.path.basename(image_path),
        "file_size": os.path.getsize(image_path),
        "file_type": Path(image_path).suffix[1:],
        "last_modified": datetime.datetime.fromtimestamp(os.path.getmtime(image_path)).isoformat(),
    }

    try:
        with Image.open(image_path) as img:
            media_metadata["dimensions"] = f"{img.width}x{img.height}"
            media_metadata["format"] = img.format
            media_metadata["mode"] = img.mode

            exif_data = {}
            if hasattr(img, '_getexif') and img._getexif():
                for tag_id, value in img._getexif().items():
                    tag = TAGS.get(tag_id, tag_id)
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8')
                        except UnicodeDecodeError:
                            value = str(value)
                    exif_data[tag] = value

                if 'DateTime' in exif_data:
                    media_metadata["date_taken"] = exif_data["DateTime"]
                if 'Model' in exif_data:
                    media_metadata["camera_model"] = exif_data["Model"]
                if 'Make' in exif_data:
                    media_metadata["camera_make"] = exif_data["Make"]
                if 'GPSInfo' in exif_data:
                    media_metadata["gps_info"] = str(exif_data["GPSInfo"])
    except Exception as e:
        logger.warning(f"EXIF extraction failed for image {image_path}: {e}")
        media_metadata["exif_error"] = str(e)

    return media_metadata

def clean_hidden_files(media_root: Path):
    removed = 0
    for subdir, _, files in os.walk(media_root):
        for filename in files:
            if filename.startswith("._") or filename.startswith("."):
                try:
                    file_path = Path(subdir) / filename
                    os.remove(file_path)
                    removed += 1
                    logger.debug(f"🧹 Removed lingering system file: {file_path}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not remove {file_path}: {e}")
    logger.info(f"🧼 Cleanup complete. {removed} hidden/system files removed.")