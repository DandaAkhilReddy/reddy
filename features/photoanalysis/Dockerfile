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
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
# Note: We need to maintain the package structure
COPY __init__.py ./
COPY config ./config
COPY models ./models
COPY services ./services
COPY utils ./utils
COPY api ./api

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
# Note: Running from /app with PYTHONPATH ensures imports work correctly
ENV PYTHONPATH=/app
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
