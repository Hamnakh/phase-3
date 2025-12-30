from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from app.config import get_settings

settings = get_settings()

# =======================
# CREATE ENGINE (NEON SAFE)
# =======================
engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
    pool_pre_ping=True,       # dead connection detect and refresh
    pool_recycle=1800,        # recycle every 30 mins
    pool_size=5,              # safe for serverless DB
    max_overflow=10,
)

# =======================
# SESSION FACTORY
# =======================
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# =======================
# INIT DB (CREATE TABLES)
# =======================
async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# =======================
# FASTAPI DEPENDENCY
# =======================
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
