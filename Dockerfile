# syntax=docker/dockerfile:1.4
# Phase 10 §10.42 — Container Security
# Minimal base image, non-root user, limited capabilities

# Use python 3.12 slim for smaller attack surface
FROM python:3.12-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    UV_SYSTEM_PYTHON=1

WORKDIR /app

# Install uv for fast dependency resolution
RUN pip install uv

# Copy package metadata
COPY pyproject.toml README.md ./

# Create non-root user for security (§10.42)
RUN groupadd -r sip && useradd -r -g sip sip

# Copy application source code
COPY ./src ./src

# Install dependencies and the package
RUN uv pip install -e .

# Ensure permissions
RUN chown -R sip:sip /app

# Switch to non-root user
USER sip

# Expose API port
EXPOSE 8000

# Healthcheck (§10.52)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Start the application
CMD ["uvicorn", "sip.api.server:app", "--host", "0.0.0.0", "--port", "8000"]
