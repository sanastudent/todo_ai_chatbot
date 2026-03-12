@echo off
setlocal enabledelayedexpansion

echo 🚀 Starting Todo AI Chatbot backend...

REM Check if virtual environment exists and activate it
if exist "venv\Scripts\activate.bat" (
    echo ✅ Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo ⚠️ Virtual environment not found, installing dependencies...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
)

REM Install requests if not already installed
pip install requests

REM Check if database migration is needed
echo 🔍 Checking database status...
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

REM Start the backend server
echo 📡 Starting backend server on port 8000...
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload