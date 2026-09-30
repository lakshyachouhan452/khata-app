import os
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# Read DATABASE_URL from environment; default to SQLite for zero-config startup
raw_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./khata.db")

# Automatically fix PostgreSQL scheme from Neon/Render/Supabase for SQLAlchemy asyncpg
if raw_url.startswith("postgres://"):
    raw_url = raw_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif raw_url.startswith("postgresql://") and not raw_url.startswith("postgresql+asyncpg://"):
    raw_url = raw_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Handle SSL query parameter differences in asyncpg (convert sslmode -> ssl)
if "sslmode=require" in raw_url:
    raw_url = raw_url.replace("sslmode=require", "ssl=require")
elif "sslmode=" in raw_url:
    import re
    raw_url = re.sub(r"sslmode=[^&]+", "ssl=require", raw_url)

DATABASE_URL = raw_url

connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args["check_same_thread"] = False

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,
    connect_args=connect_args,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
