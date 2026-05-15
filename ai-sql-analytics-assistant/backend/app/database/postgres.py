from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings


# DATABASE_URL must use the asyncpg driver:
# postgresql+asyncpg://user:pass@host:5432/dbname
if not settings.DATABASE_URL.startswith("postgresql+asyncpg://"):
    raise ValueError(
        f"DATABASE_URL must use 'postgresql+asyncpg://' scheme for async support. "
        f"Got: {settings.DATABASE_URL!r}"
    )

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=(settings.APP_ENV == "development"),
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """FastAPI dependency — yields an async DB session."""
    async with AsyncSessionLocal() as session:
        yield session