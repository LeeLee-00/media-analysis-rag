# app/core/elasticsearch.py
from elasticsearch import Elasticsearch
from app.core.config import ELASTIC_HOST, ELASTIC_INDEX, VECTOR_DIMS
from app.core.logging.logger import get_logger

logger = get_logger(__name__)

es = Elasticsearch(ELASTIC_HOST)

async def init_elasticsearch():
    try:
        if es.indices.exists(index=ELASTIC_INDEX):
            # es.indices.delete(index=ELASTIC_INDEX)
            # logger.warning(f"Deleted old Elasticsearch index: {ELASTIC_INDEX}")
            pass

        mapping = {
            "mappings": {
                "properties": {
                    "filename": {"type": "keyword"},
                    "media_type": {"type": "keyword"},
                    "summary": {"type": "text"},
                    "transcript": {"type": "text"},
                    "relative_path": {"type": "keyword"},
                    "timestamp": {"type": "date"},
                    "vector": {
                        "type": "dense_vector",
                        "dims": VECTOR_DIMS
                    }
                }
            }
        }

        es.indices.create(index=ELASTIC_INDEX, body=mapping)
        logger.info(f"✅ Created Elasticsearch index '{ELASTIC_INDEX}'")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Elasticsearch: {e}")
