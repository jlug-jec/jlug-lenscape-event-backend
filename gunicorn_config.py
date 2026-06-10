"""
Gunicorn production configuration for Lenscape API.

Usage:
    gunicorn -c gunicorn_config.py wsgi:app
"""
import os
import multiprocessing

# Bind to the port provided by the platform (Render/Railway/Heroku set $PORT)
port = os.getenv("PORT", os.getenv("FLASK_PORT", "5000"))
bind = f"0.0.0.0:{port}"

# Worker processes. Default: (2 x CPU) + 1, override with WEB_CONCURRENCY.
workers = int(os.getenv("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2 + 1))

# Threads per worker — gthread allows concurrency for I/O-bound Firestore calls.
threads = int(os.getenv("GUNICORN_THREADS", 4))
worker_class = "gthread"

# Timeouts
timeout = int(os.getenv("GUNICORN_TIMEOUT", 60))
graceful_timeout = 30
keepalive = 5

# Recycle workers periodically to avoid memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging to stdout/stderr (captured by the hosting platform)
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")

# Preload app so Firebase/Firestore init happens once before forking workers
preload_app = True
