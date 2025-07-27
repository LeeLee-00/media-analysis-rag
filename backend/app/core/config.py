import os
import tempfile
from pathlib import Path
from dotenv import load_dotenv

# ----------------------------------------
# Load Environment Variables
# ----------------------------------------
load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# ----------------------------------------
# Logging Configuration
LOG_PATH = os.getenv("LOG_PATH", "logs/ingest_logs.log")

# ----------------------------------------

# ----------------------------------------
# Filesystem Paths
# ----------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMP_DIR = os.path.join(tempfile.gettempdir(), "media_analysis_api")
os.makedirs(TEMP_DIR, exist_ok=True)
CLEANUP_TEMP_FILES = True

# ----------------------------------------
# API Metadata
# ----------------------------------------
API_TITLE = "Media Analysis API"
API_DESCRIPTION = "API for analyzing images and videos using AI"
API_VERSION = "1.0.0"

# ----------------------------------------
# AI Model Configurations
# ----------------------------------------
MAX_FRAME_COUNT = 3
MIN_SUMMARY_LENGTH = 50
MAX_SUMMARY_LENGTH = 125

# ----------------------------------------
# PostgreSQL Config
# ----------------------------------------
WRITE_TO_PG = os.getenv("WRITE_TO_PG", False)
POSTGRES_USER = os.getenv("POSTGRES_USER", 'postgres')
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", 'postgres_password')
POSTGRES_DB = os.getenv("POSTGRES_DB", 'postgres')
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# ----------------------------------------
# Elasticsearch Config
# ----------------------------------------
ELASTIC_HOST = os.getenv("ELASTIC_HOST", "http://localhost:9200")
ELASTIC_INDEX = os.getenv("ELASTIC_INDEX", "media_index")
VECTOR_DIMS = int(os.getenv("VECTOR_DIMS", 384))

# ----------------------------------------
#  External Storage Config
MEDIA_ROOT = "/volumes/easystore/DC_25_data"
# ----------------------------------------
