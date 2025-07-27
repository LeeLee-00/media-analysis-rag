FROM python:3.11-slim

# Install system dependencies including libraries and tools needed by your app
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    build-essential \
    poppler-utils \
    curl \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*


# # Install Ollama Linux binary (adjust version and URL as needed)
# RUN curl -fsSL https://ollama.com/install.sh | sh

# # # Create directory for Ollama models
# # RUN mkdir -p /root/.ollama/models

# Install Python dependencies first (better layer caching)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r /app/requirements.txt

# Set working directory and copy the entire application code
WORKDIR /app
COPY . /app

# RUN ollama pull llama3:8b
# RUN ollama pull llama3.2-vision:11b

# Default command if no override is provided (will be overridden by docker-compose)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

