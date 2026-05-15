import redis.asyncio as aioredis
from app.core.config import settings

# Module-level client — initialized lazily on first use via get_redis()
_redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    """
    Returns the module-level async Redis client.
    Raises a clear RuntimeError if the connection cannot be established.
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )
        try:
            await _redis_client.ping()
        except Exception as exc:
            _redis_client = None
            raise RuntimeError(
                f"Cannot connect to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}. "
                f"Error: {exc}"
            ) from exc
    return _redis_client


async def close_redis() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
