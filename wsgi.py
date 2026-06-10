"""
WSGI entry point for production servers (Gunicorn).

Run in production:
    gunicorn -c gunicorn_config.py wsgi:app

Run in development instead:
    python app.py
"""
from app import app

if __name__ == "__main__":
    app.run()
