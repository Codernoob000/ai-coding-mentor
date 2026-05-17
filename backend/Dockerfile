# Stage 1: Build Dependencies
FROM python:3.12-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Install to a prefix to make copying easier
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# --- Stage 2: Hardened Runtime ---
FROM python:3.12-slim

WORKDIR /app

# 1. Security: Create a restricted non-root user with a home directory
RUN groupadd -r appuser && useradd -r -m -g appuser -s /sbin/nologin appuser

# 2. Copy dependencies from builder
# We copy to /usr/local to ensure they are in the default Python path
COPY --from=builder /install /usr/local

# 3. Copy application source
# Ensure appuser owns the code and the workspace
COPY --chown=appuser:appuser ./app ./app

# 4. Environment Hardening
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

# 5. Persistence setup (Initialize local DB with correct permissions)
RUN touch mentor_agent.db && chown appuser:appuser mentor_agent.db

# 6. Security: Switch to non-root user
USER appuser

# Cloud Run defaults to 8080
EXPOSE 8080

# 7. Production Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python3 -c "import http.client; import sys; c = http.client.HTTPConnection('localhost', 8080); c.request('GET', '/api/v1/health'); sys.exit(0 if c.getresponse().status == 200 else 1)"

# 8. Optimized Uvicorn Execution
# Using 1 worker for Cloud Run is often preferred to allow the platform to scale pods
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8080", \
     "--proxy-headers", \
     "--forwarded-allow-ips", "*", \
     "--timeout-keep-alive", "60", \
     "--no-access-log"]
