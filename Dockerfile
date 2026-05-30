FROM python:3.12-slim
WORKDIR /app
# Install system dependencies for ChromaDB and Ollama client
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*
# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy the entire backend code
COPY backend/app ./app
COPY backend/agents ./agents
COPY backend/ingest.py .
# Create data directories
RUN mkdir -p /app/data/raw /app/data/chroma_db /app/data/memory_cache
# Expose port
EXPOSE 8000
# Command to run FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
