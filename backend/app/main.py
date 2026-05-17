from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logger import setup_logging, logger, correlation_id
from app.infrastructure.database import engine, Base
from app.api.v1.routers import chat
from app.api.middleware import LoggingMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Initialize high-performance structured logging
    setup_logging()
    logger.info(f"System boot: {settings.APP_NAME} in {settings.ENVIRONMENT} mode")
    
    # 2. Automated Schema Creation (SQLite Local Dev only)
    # In production, use Alembic migrations.
    try:
        logger.info("Initializing database schema...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema initialized.")
    except Exception as e:
        logger.critical(f"Database initialization failed: {e}", exc_info=True)
    
    yield
    logger.info("System shutdown initiated")

app = FastAPI(
    title=settings.APP_NAME,
    description="A Personalized AI Coding Mentor Agent powered by Gemini",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # CRITICAL FIX: Use the ContextVar directly for the response to ensure ID consistency
    request_id = correlation_id.get()
    logger.error(f"Global Exception Handler: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected server error occurred.",
            "request_id": request_id
        }
    )

app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_config=None)
