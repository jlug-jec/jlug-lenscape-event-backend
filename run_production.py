import os
from dotenv import load_dotenv
from app import app
from waitress import serve

# Load environmental configs
load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    print(f"Starting Lenscape API in PRODUCTION mode with Waitress WSGI...")
    print(f"Serving on http://0.0.0.0:{port} with 50 multi-threaded worker channels...")
    
    # Start waitress server with scale configurations
    serve(
        app,
        host="0.0.0.0",
        port=port,
        threads=50,              # Allow up to 50 active worker threads to process concurrent requests
        connection_limit=1000,   # Maximum total concurrent TCP sockets open
        channel_timeout=30       # Drop socket channel if idle for more than 30s
    )
