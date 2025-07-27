# Media Analysis RAG: Multimodal Image & Video Analysis with RAG Search

## 🚩 Overview

This project provides an end-to-end platform for analyzing images and videos using AI, generating descriptive summaries, transcripts, and metadata, and enabling advanced search and retrieval via Retrieval-Augmented Generation (RAG). The system is designed for analysts and researchers to efficiently query and explore large volumes of visual and audio-visual data.

---

## 📦 Architecture

- **Frontend:** Streamlit app for uploading media, running analysis, and performing RAG/keyword searches.
- **Backend:** FastAPI API for media ingestion, AI-powered analysis, and search endpoints.
- **AI Models:** Ollama (Llama 3, Llama 3.2 Vision), Whisper for transcription, Sentence Transformers for embeddings.
- **Database:** PostgreSQL for structured storage, Elasticsearch for vector and keyword search.
- **Orchestration:** Docker Compose for multi-service deployment.

---

## 🛠️ Technologies

- **Backend:** FastAPI, SQLAlchemy, Elasticsearch, PostgreSQL, Ollama, Whisper, Sentence Transformers, OpenCV, Pillow, MoviePy
- **Frontend:** Streamlit, Requests
- **AI Models:** Llama 3, Llama 3.2 Vision (via Ollama), Whisper (speech-to-text)
- **DevOps:** Docker, Docker Compose

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/media-analysis-rag.git
cd media-analysis-rag
```

### 2. Launch with Docker Compose

```bash
docker-compose up --build
```

- **Frontend:** [http://localhost:8080](http://localhost:8080)
- **Backend:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Elasticsearch:** [http://localhost:9200](http://localhost:9200)
- **Postgres:** [localhost:5432](localhost:5432)

> **Note:** Ollama models (Llama 3, Llama 3.2 Vision) are pulled automatically on first run.

---

## 🖥️ Usage

### Frontend (Streamlit)

- **Home:** Welcome page with project overview.
- **Media Analysis:** Upload images/videos for AI-powered summary, transcript, and metadata extraction.
- **RAG/Keyword Search:** Ask questions or search keywords across your analyzed media.

### Backend (FastAPI)

- `/upload/media`: Upload and analyze image or video (auto-detects type).
- `/analyze/image`: Analyze an image file.
- `/analyze/video`: Analyze a video file.
- `/search/media`: Keyword search across summaries and transcripts.
- `/rag/custom`: RAG search endpoint for question answering.
- `/health`: Health check endpoint.

### Data Flow

1. **Upload Media:** User uploads a file via the frontend.
2. **Analysis:** Backend extracts keyframes, captions, transcripts, and metadata using AI models.
3. **Storage:** Results are stored in PostgreSQL and indexed in Elasticsearch with vector embeddings.
4. **Search:** Users can search using keywords or natural language questions (RAG).

---

## ⚙️ Configuration

- **Environment Variables:** See `backend/app/core/config.py` for all configurable options (DB, Elasticsearch, Ollama, etc).
- **Media Storage:** Update `MEDIA_ROOT` in backend config for your media directory.
- **Ollama:** Ollama runs as a service and is used for both vision and text models.

---

## 🧪 Development

- **Linting:** Uses [Ruff](https://github.com/charliermarsh/ruff) (`ruff check .`)
- **Testing:** (WIP)
- **Logs:** Backend logs to `logs/ingest_logs.log` by default.

---

## 📚 Project Structure

```
media-analysis-rag/
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI endpoints
│   │   ├── core/          # Config, logging, AI models, utils
│   │   ├── models/        # SQLAlchemy models
│   │   └── services/      # Analysis, storage, RAG logic
│   ├── scripts/           # Batch ingestion scripts
│   └── requirements.txt
├── frontend/
│   ├── view/              # Streamlit page modules
│   ├── classes/           # API client and utilities
│   ├── app.py             # Streamlit entrypoint
│   └── requirements.txt
├── docker-compose.yml
├── entrypoint.sh          # Ollama model pull script
└── README.md
```

---

## 📝 Notes

- **Batch Ingestion:** Use `backend/scripts/batch_ingest_media.py` for large-scale video ingestion.
- **GPU Support:** Ollama and Whisper can leverage GPU if available (see Docker Compose comments).
- **Extensibility:** Add new AI models or search strategies by extending backend services.

---

## 🆘 Troubleshooting

- **Backend Connection:** Use the "Test Backend Connection" button in the Streamlit sidebar.
- **Ollama Models:** If models fail to pull, check Ollama logs or run `ollama pull llama3:8b` manually inside the container.
- **Elasticsearch/DB:** Ensure containers are healthy (`docker ps` and logs).

---

For further assistance, see the code comments or open an issue on the GitHub repository.
