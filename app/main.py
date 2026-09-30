from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router as api_router
from app.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # Startup: Create tables if database connection is available
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("INFO: Database tables verified and initialized successfully.")
    except Exception as e:
        print(f"WARNING: Database initialization encountered an error: {e}")
    yield
    # Shutdown: Clean up database engine connections
    try:
        await engine.dispose()
    except Exception:
        pass


app = FastAPI(
    title="Khata Ledger API",
    description="Digital ledger and credit management web application backend for shopkeepers.",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for web frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router
app.include_router(api_router, prefix="/api")


@app.get("/", tags=["Health"])
async def root():
    return {
        "app": "Khata Ledger API",
        "status": "online",
        "docs_url": "/docs",
        "endpoints": {
            "customers": "/api/customers/",
            "transactions": "/api/transactions/",
            "expected_next_7_days": "/api/transactions/expected-in-next-7-days",
            "overdue_customers": "/api/customers/overdue",
        },
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}
