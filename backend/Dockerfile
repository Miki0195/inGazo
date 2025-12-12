# InGazo Backend Dockerfile
# Multi-stage build for optimized production image

# Stage 1: Base image with system dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for GeoDjango and PostGIS
RUN apt-get update && apt-get install -y --no-install-recommends \
    # PostgreSQL client
    libpq-dev \
    # GDAL dependencies for GeoDjango
    gdal-bin \
    libgdal-dev \
    # GEOS for geometric operations
    libgeos-dev \
    # PROJ for coordinate transformations
    libproj-dev \
    # Build essentials
    gcc \
    g++ \
    # Cleanup
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set GDAL environment variables
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal \
    C_INCLUDE_PATH=/usr/include/gdal

# Stage 2: Builder for Python dependencies
FROM base as builder

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-warn-script-location -r requirements.txt

# Stage 3: Production image
FROM base as production

# Create non-root user for security
RUN groupadd --gid 1000 ingazo \
    && useradd --uid 1000 --gid ingazo --shell /bin/bash --create-home ingazo

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/ingazo/.local
ENV PATH=/home/ingazo/.local/bin:$PATH

# Copy application code
COPY --chown=ingazo:ingazo . .

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media /app/logs \
    && chown -R ingazo:ingazo /app

# Switch to non-root user
USER ingazo

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/docs/')" || exit 1

# Default command
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--worker-class", "gthread", "--worker-tmp-dir", "/dev/shm", "--access-logfile", "-", "--error-logfile", "-", "core.wsgi:application"]

# Stage 4: Development image
FROM base as development

WORKDIR /app

# Install development dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media /app/logs

# Expose port
EXPOSE 8000

# Development command with hot reload
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

