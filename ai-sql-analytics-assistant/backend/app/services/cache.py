"""
cache.py
--------
Redis-based query result cache.
Key: SHA256(dataset_id + ":" + prompt)
Value: JSON-serialized (columns, rows)
TTL: CACHE_TTL seconds (from settings)
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

from app.database.redis import get_redis
from app.core.config import settings


def _make_cache_key(dataset_id: int, prompt: str) -> str:
    raw = f"{dataset_id}:{prompt.strip().lower()}"
    return "schemaiq:query:" + hashlib.sha256(raw.encode()).hexdigest()


async def get_cached_result(
    dataset_id: int, prompt: str
) -> tuple[list[str], list[dict]] | None:
    """
    Returns (columns, rows) if cached, else None.
    Raises RuntimeError if Redis is unreachable (surfaced to caller).
    """
    redis = await get_redis()
    key = _make_cache_key(dataset_id, prompt)
    raw = await redis.get(key)
    if raw is None:
        return None
    payload = json.loads(raw)
    return payload["columns"], payload["rows"]


async def set_cached_result(
    dataset_id: int,
    prompt: str,
    columns: list[str],
    rows: list[dict[str, Any]],
) -> None:
    """
    Store query results in Redis with CACHE_TTL expiry.
    Raises RuntimeError if Redis is unreachable (surfaced to caller).
    """
    redis = await get_redis()
    key = _make_cache_key(dataset_id, prompt)
    payload = json.dumps({"columns": columns, "rows": rows})
    await redis.setex(key, settings.CACHE_TTL, payload)
