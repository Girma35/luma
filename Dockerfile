# ══════════════════════════════════════════════════════════════
# ReOrder AI — Production Dockerfile (API only)
# Build:  docker build -t reorder-api .
# Run:    docker run -p 8000:8000 --env-file .env reorder-api
# ══════════════════════════════════════════════════════════════

FROM python:3.11-slim AS base

# Security: don't run as root
RUN groupadd -r app && useradd -r -g app app

WORKDIR /app

# Install deps first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini gunicorn.conf.py ./

# Own files by app user
RUN chown -R app:app /app
USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/health')" || exit 1

CMD ["gunicorn", "-c", "gunicorn.conf.py", "src.api.main:app"]
