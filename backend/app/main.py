import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_v1_router
from app.core import Base, engine, settings
from app.tasks.scheduler import periodic_overdue_checker_task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("khata.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # 1. Startup: Create tables if not present
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info(f"Database initialized successfully using: {settings.DATABASE_URL.split('@')[-1]}")
    except Exception as e:
        logger.warning(
            f"Database initialization warning: {e}. The server will start, but check your DATABASE_URL."
        )

    # 2. Background task: Periodic overdue transactions checker
    task = asyncio.create_task(periodic_overdue_checker_task(interval_seconds=3600))

    yield

    # 3. Shutdown: Cancel background tasks and dispose DB pool
    task.cancel()
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Digital ledger and credit management web application backend for shopkeepers.",
    lifespan=lifespan,
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API v1 Router
app.include_router(api_v1_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Health"])
async def root():
    return {
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR,
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}
