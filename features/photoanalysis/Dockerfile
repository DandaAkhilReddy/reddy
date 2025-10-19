# ReddyFit Photo Analysis API - Production Dockerfile
# Python 3.11 for MediaPipe compatibility

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies required for OpenCV and MediaPipe
RUN apt-get update && apt-get install -y --no-install-recommends \
    # OpenCV dependencies (updated for Debian Trixie)
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    # Additional libraries for image processing
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
    # General utilities
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt ./photoanalysis/

# Install Python dependencies
RUN pip install --no-cache-dir -r ./photoanalysis/requirements.txt

# Copy application code as a package
# Maintains proper Python package structure for relative imports
COPY __init__.py ./photoanalysis/
COPY config ./photoanalysis/config
COPY models ./photoanalysis/models
COPY services ./photoanalysis/services
COPY utils ./photoanalysis/utils
COPY api ./photoanalysis/api

# Create necessary directories
RUN mkdir -p /app/logs /app/cache

# Note: .env file not needed - using Fly.io secrets instead

# Expose port (Fly.io uses PORT environment variable)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run the application with uvicorn
# Use exec form to ensure proper signal handling
# Run from /app so photoanalysis is a proper Python package
CMD ["python", "-m", "uvicorn", "photoanalysis.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
