from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime
from typing import AsyncGenerator
from contextlib import asynccontextmanager
import os
import time
import logging
import traceback
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

from src.services.database import get_async_session, async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from src.api.routes import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler to manage app startup and shutdown
    """
    # Startup
    print("Starting up the application...")
    yield
    # Shutdown
    print("Shutting down the application...")
    await async_engine.dispose()


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application
    """
    app = FastAPI(
        title="Todo AI Chatbot API",
        description="API for the Todo AI Chatbot with MCP integration",
        version="0.1.0",
        lifespan=lifespan
    )

    # Add request logging middleware
    @app.middleware("http")
    async def log_requests(request, call_next):
        print(f"[BACKEND LOG] Incoming: {request.method} {request.url.path}")  # Added for debugging
        start_time = time.time()

        # Get client IP
        client_host = request.client.host
        client_port = request.client.port

        # Log the incoming request
        logging.info(f"Request: {request.method} {request.url.path} from {client_host}:{client_port}")

        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            status_code = response.status_code

            # Log the response
            logging.info(f"Response: {status_code} in {process_time:.2f}s for {request.method} {request.url.path}")

            return response
        except Exception as e:
            process_time = time.time() - start_time
            # Log the error
            logging.error(f"Error processing {request.method} {request.url.path}: {str(e)} in {process_time:.2f}s")
            raise

    # Add CORS middleware
    origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000,http://localhost:5174").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add exception handlers for JSON responses
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc),
                "type": type(exc).__name__
            }
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        return JSONResponse(
            status_code=422,
            content={"error": "Validation error", "details": exc.errors()}
        )

    # Include API routes
    app.include_router(api_router)

    return app


# Create the main application instance
app = create_app()


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running
    """
    from fastapi.responses import JSONResponse
    return JSONResponse(
        content={"status": "healthy", "timestamp": datetime.utcnow().isoformat()},
        status_code=200
    )


# Dependency for database sessions
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(async_engine) as session:
        yield session


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=True
    )