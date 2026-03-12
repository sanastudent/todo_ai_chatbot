import os
import sys
sys.path.insert(0, os.path.join(os.getcwd(), '.'))

from src.main import app
import uvicorn

if __name__ == "__main__":
    # Set environment variables for the server
    os.environ.setdefault("API_HOST", "0.0.0.0")
    os.environ.setdefault("API_PORT", "8001")
    os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./todo_chatbot_dev.db")

    print("Starting server on port 8001...")
    uvicorn.run(
        app,
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8001")),
        log_level="debug"
    )