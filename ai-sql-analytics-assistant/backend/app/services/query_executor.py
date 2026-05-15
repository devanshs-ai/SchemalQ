"""
query_executor.py
-----------------
Executes validated SQL against the user's dynamic dataset table.
Returns structured results — raises HTTPException on DB errors.
"""
from __future__ import annotations

import time
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException


async def execute_query(
    db: AsyncSession,
    sql: str,
) -> tuple[list[str], list[dict[str, Any]], int]:
    """
    Execute a validated SQL query.

    Returns
    -------
    (columns, rows, execution_time_ms)
        columns          — list of column name strings
        rows             — list of dicts (column_name → value)
        execution_time_ms — wall-clock time in milliseconds

    Raises
    ------
    HTTPException(422)
        On SQL execution errors (e.g. unknown column, type mismatch).
    """
    start = time.monotonic()

    try:
        result = await db.execute(text(sql))
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=(
                f"SQL execution failed.\n"
                f"Query: {sql!r}\n"
                f"Error: {exc}"
            ),
        )

    elapsed_ms = int((time.monotonic() - start) * 1000)

    columns = list(result.keys())
    raw_rows = result.fetchall()

    rows = [
        {col: _serialize_value(val) for col, val in zip(columns, row)}
        for row in raw_rows
    ]

    return columns, rows, elapsed_ms


def _serialize_value(value: Any) -> Any:
    """Convert non-JSON-serializable types to strings."""
    if value is None:
        return None
    if isinstance(value, (int, float, bool, str)):
        return value
    # Dates, datetimes, Decimals, etc.
    return str(value)
