# app/core/prompts/prompt_templates.py

def image_prompt(caption: str, ocr_text: str = "") -> str:
    """
    Builds a prompt for summarizing image content, including optional OCR text.
    """
    prompt = (
        "You are analyzing an image. Your goal is to describe the visual content clearly and concisely.\n\n"
        f"Visual Description:\n{caption.strip()}\n"
    )
    if ocr_text.strip():
        prompt += f"\nExtracted Text (OCR):\n{ocr_text.strip()}\n"

    prompt += "\nGenerate a concise summary:"
    return prompt


def video_prompt(visual_captions: str, audio_transcript: str = "") -> str:
    """
    Builds a prompt for summarizing a video using visual and audio content.
    """
    prompt = (
        "You are analyzing a video that contains both visual scenes and spoken audio.\n"
        "Summarize the main points based on both modalities in a clear and neutral tone.\n\n"
        f"Visual Captions:\n{visual_captions.strip()}\n"
    )
    if audio_transcript.strip():
        prompt += f"\nAudio Transcript:\n{audio_transcript.strip()}\n"

    prompt += "\nGenerate a clear and concise summary:"
    return prompt
