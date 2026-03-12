#!/bin/bash
# Startup script for the Todo AI Chatbot backend

set -e  # Exit on any error

echo "🚀 Starting Todo AI Chatbot backend..."

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    echo "✅ Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️ Virtual environment not found, installing dependencies..."
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
fi

# Install requests if not already installed
pip install requests

# Check if database migration is needed
echo "🔍 Checking database status..."
python -c "
import asyncio
from src.init_db import init_db

async def check_and_init_db():
    try:
        print('Attempting to initialize database...')
        await init_db()
        print('Database initialization completed successfully!')
    except Exception as e:
        print(f'Database initialization failed: {e}')
        return False
    return True

result = asyncio.run(check_and_init_db())
exit(0 if result else 1)
"

# Start the backend server
echo "📡 Starting backend server on port 8001..."
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload