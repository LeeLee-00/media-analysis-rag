# app/services/rag_search.py
from pydantic import BaseModel, Field
from typing import List, Optional
from logging import getLogger

logger = getLogger(__name__)

class RAGQuery(BaseModel):
    query: str
    prompt_template: Optional[str] = Field(
        default="Based on the following media files and their summaries/transcripts, answer the question:"
    )
    top_k: int = 5
    score_threshold: float = 1.25
    fallback_to_keyword: bool = True
    debug: bool = True

def build_context_from_docs(docs: List[dict]) -> str:
    if not docs:
        return "No relevant documents were found to support the answer.\n"
    return "\n---\n".join(
        f"Filename: {d['filename']}\nMedia Type: {d['media_type']}\nSummary: {d['summary']}\nTranscript: {d['transcript']}\n"
        for d in docs
    )

def chunk_text(text: str, max_chars: int = 1000) -> List[str]:
    chunks = []
    while len(text) > max_chars:
        split_at = text.rfind(". ", 0, max_chars) + 1
        if split_at == 0:
            split_at = max_chars
        chunks.append(text[:split_at].strip())
        text = text[split_at:].strip()
    if text:
        chunks.append(text)
    return chunks

def run_rag_pipeline(
    query: str,
    top_k: int = 5,
    score_threshold: float = 1.25,
    fallback_to_keyword: bool = True,
    debug: bool = False
) -> dict:
    from app.core.elasticsearch import es
    from app.core.config import ELASTIC_INDEX
    from app.core.ai_models import get_model_loader

    logger.info(f"🔍 Running RAG pipeline for query: '{query}'")
    model_loader = get_model_loader()
    query_vector = model_loader.embed_query(query)

    try:
        # Vector search
        response = es.search(
            index=ELASTIC_INDEX,
            body={
                "size": top_k,
                "query": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'vector') + 1.0",
                            "params": {"query_vector": query_vector}
                        }
                    }
                }
            }
        )

        hits = response["hits"]["hits"]
        logger.info(f"✅ Retrieved {len(hits)} vector search hits")

        filtered_docs = [
            {
                "filename": hit["_source"]["filename"],
                "media_type": hit["_source"].get("media_type", "unknown"),
                "relative_path": hit["_source"].get("relative_path", ""),
                "summary": hit["_source"].get("summary", ""),
                "transcript": hit["_source"].get("transcript", ""),
                "score": hit["_score"]
            }
            for hit in hits if hit["_score"] > score_threshold
        ][:2]

        # Fallback to keyword if needed
        if not filtered_docs and fallback_to_keyword:
            logger.info("🔁 Fallback to keyword search")
            keyword_response = es.search(
                index=ELASTIC_INDEX,
                body={
                    "size": top_k,
                    "query": {
                        "multi_match": {
                            "query": query,
                            "fields": ["summary", "transcript"]
                        }
                    }
                }
            )
            keyword_hits = keyword_response["hits"]["hits"]
            filtered_docs = [
                {
                    "filename": hit["_source"]["filename"],
                    "media_type": hit["_source"].get("media_type", "unknown"),
                    "relative_path": hit["_source"].get("relative_path", ""),
                    "summary": hit["_source"].get("summary", ""),
                    "transcript": hit["_source"].get("transcript", ""),
                    "score": hit["_score"]
                }
                for hit in keyword_hits
            ][:2]

        # Build prompt for Ollama summarization
        combined_text = "\n\n".join(
            f"{doc['summary']}\n{doc['transcript']}" for doc in filtered_docs
        )

        full_prompt = f"""
        You are an expert assistant helping to answer questions based on media files.

        Context:
        {combined_text}

        Question:
        {query}

        Answer:
        """.strip()

        answer = model_loader.summarize_text(text=full_prompt, prompt=None)

        return {
            "query": query,
            "answer": answer.strip(),
            "supporting_documents": filtered_docs,
            "rag_prompt": full_prompt if debug else None
        }

    except Exception as e:
        logger.exception("❌ Error in RAG pipeline")
        raise RuntimeError(f"RAG pipeline failed: {e}")
