import os
import time
import torch
import whisper
from typing import Optional
from sentence_transformers import SentenceTransformer
from ollama import Client
from app.core.logging.logger import get_logger

logger = get_logger(__name__)

_verified_models = set()

def ensure_ollama_model(client: Client, model_name: str, retries: int = 3, delay: int = 5):
    if model_name in _verified_models:
        return
    for attempt in range(1, retries + 1):
        try:
            installed_models = client.list().get("models", [])
            if not any(getattr(m, "name", "").startswith(model_name) for m in installed_models):
                logger.info(f"Pulling model '{model_name}' via Ollama API...")
                client.pull(model_name)
                logger.info(f"✅ Model '{model_name}' successfully pulled.")
            else:
                logger.info(f"✅ Model '{model_name}' already installed.")
            _verified_models.add(model_name)
            return
        except Exception as e:
            logger.error(f"Attempt {attempt}: Error ensuring model '{model_name}': {e}")
            time.sleep(delay)
    raise RuntimeError(f"Could not verify or pull model '{model_name}' after {retries} attempts.")

class OllamaModelLoader:
    def __init__(self):
        env = os.getenv("ENV", "prod")
        default_host = "http://host.docker.internal:11434" if env == "dev" else "http://ollama:11434"
        ollama_host = os.getenv("OLLAMA_HOST", default_host)
        self.client = Client(host=ollama_host)

        try:
            ensure_ollama_model(self.client, "llama3:8b")
            ensure_ollama_model(self.client, "llama3.2-vision:11b")
        except Exception as e:
            logger.error(f"Model verification failed: {e}")

        if torch.backends.mps.is_available():
            self.device = "mps"
        elif torch.cuda.is_available():
            self.device = "cuda"
        else:
            self.device = "cpu"
        logger.info(f"Using device: {self.device}")

        try:
            self.whisper_model = whisper.load_model("base")
            logger.info("✅ Whisper loaded.")
        except Exception as e:
            logger.warning(f"⚠️ Whisper fallback: {e}")
            self.whisper_model = type("DummyWhisper", (), {"transcribe": lambda _, __: {"text": "N/A"}})()

        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    def vision_infer(self, image_path: str, prompt: str) -> str:
        with open(image_path, "rb") as img:
            image_bytes = img.read()
        response = self.client.chat(
            model="llama3.2-vision:11b",
            messages=[{
                "role": "user",
                "content": prompt,
                "images": [image_bytes]
            }]
        )
        return response["message"]["content"]
    
    def summarize_text(self, text: str, prompt: Optional[str] = None) -> str:
        full_input = f"{prompt}\n\n{text}" if prompt else text
        response = self.client.chat(
            model="llama3:8b",
            messages=[{
                "role": "user",
                "content": full_input
            }]
        )
        return response["message"]["content"]


    def transcribe_audio(self, audio_path: str) -> str:
        result = self.whisper_model.transcribe(audio_path)
        return result.get("text", "").strip()

    def embed_query(self, text: str):
        return self.embedding_model.encode(text, normalize_embeddings=True).tolist()

_model_loader_instance = None

def get_model_loader():
    global _model_loader_instance
    if _model_loader_instance is None:
        _model_loader_instance = OllamaModelLoader()
    return _model_loader_instance
