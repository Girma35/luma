# Gunicorn configuration for production
# Usage: gunicorn -c gunicorn.conf.py src.api.main:app

import multiprocessing
import os

# Bind
bind = "127.0.0.1:8000"

# Workers — 2 is fine for 1 vCPU / 2 GB Droplet
workers = int(os.getenv("GUNICORN_WORKERS", 2))
worker_class = "uvicorn.workers.UvicornWorker"

# Timeouts
timeout = 120
graceful_timeout = 30
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info").lower()

# Security
limit_request_line = 8190
limit_request_fields = 100
limit_request_field_size = 8190

# Process naming
proc_name = "reorder-ai-api"

# Preload app for faster worker spawning (shared memory)
preload_app = True
