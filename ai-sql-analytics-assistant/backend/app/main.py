from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.postgres import engine
from app.database.base import Base
from app.database.redis import close_redis

# Import all models so Base.metadata knows about them before create_all
import app.models  # noqa: F401

from app.api.upload import router as upload_router
from app.api.query import router as query_router
from app.api.datasets import router as datasets_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: create all ORM tables if they don't exist.
    Shutdown: close Redis connection pool.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await close_redis()


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="AI-powered natural language to SQL analytics platform.",
    lifespan=lifespan,
)

# CORS — allow configured origins (default: * for dev)
origins = (
    [o.strip() for o in settings.ALLOWED_ORIGINS.split(",")]
    if settings.ALLOWED_ORIGINS != "*"
    else ["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(upload_router)
app.include_router(query_router)
app.include_router(datasets_router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "service": settings.APP_NAME,
        "version": "1.0.0",
        "status": "running",
        "env": settings.APP_ENV,
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}