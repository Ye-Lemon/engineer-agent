import os
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from dotenv import load_dotenv


# Resolve .env from the project directory instead of the process working directory.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        f"DATABASE_URL is not configured. Set it in {BASE_DIR / '.env'} "
        "or in the process environment."
    )

async_engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True
)
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
