# ─────────────────────────────────────────────────────────────
# Multi-Stage / Production Dockerfile for Customer Review Analyzer
# ─────────────────────────────────────────────────────────────

# 1. Base Image: Official lightweight Python 3.11 Debian Linux
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (curl for healthchecks, libpq for PostgreSQL)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy dependencies first (enables Docker layer caching for faster builds)
COPY requirements.txt .

# Install all production dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Download required NLP language models inside the container
RUN python -m spacy download en_core_web_sm && \
    python -m nltk.downloader -d /usr/local/share/nltk_data opinion_lexicon

# 3. Copy application code into container
COPY . .

# Expose Streamlit default port
EXPOSE 8501

# Health check to verify Streamlit is responding
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Default command to run the Streamlit app
ENTRYPOINT ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
