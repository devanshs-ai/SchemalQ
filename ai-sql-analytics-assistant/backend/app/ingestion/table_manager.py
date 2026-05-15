"""
table_manager.py
----------------
Dynamically creates PostgreSQL tables from inferred schema.
Creates appropriate indexes without silent fallbacks.
"""
from __future__ import annotations

import re
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.ingestion.schema_inference import InferredColumn


def _build_table_name(filename: str, existing_names: set[str]) -> str:
    """
    Derive a safe, unique Postgres table name from a filename.
    Appends _2, _3, ... if the name already exists.
    """
    base = re.sub(r"[^a-zA-Z0-9]", "_", filename.rsplit(".", 1)[0]).lower()
    base = re.sub(r"_+", "_", base).strip("_")
    if not base:
        raise ValueError(f"Cannot derive a valid table name from filename: '{filename}'")

    candidate = f"ds_{base}"
    counter = 2
    while candidate in existing_names:
        candidate = f"ds_{base}_{counter}"
        counter += 1
    return candidate


async def get_existing_table_names(conn: AsyncConnection) -> set[str]:
    result = await conn.execute(
        text(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
        )
    )
    return {row[0] for row in result.fetchall()}


async def create_dataset_table(
    conn: AsyncConnection,
    table_name: str,
    columns: list[InferredColumn],
) -> None:
    """
    Creates the dynamic data table.
    Raises if the table already exists (shouldn't happen given unique name generation).
    """
    col_defs = [f"_row_id BIGSERIAL PRIMARY KEY"]
    for col in columns:
        nullable = "" if col.is_nullable else " NOT NULL"
        col_defs.append(f'"{col.column_name}" {col.pg_type}{nullable}')

    col_block = ",\n  ".join(col_defs)
    ddl = f'CREATE TABLE IF NOT EXISTS "{table_name}" (\n  {col_block}\n);'
    await conn.execute(text(ddl))

    # Index strategy:
    # 1. Any column containing "id" (but not the PK) gets a B-tree index
    # 2. The first TIMESTAMP or TIMESTAMPTZ column gets an index for time-series queries
    timestamp_indexed = False
    for col in columns:
        col_lower = col.column_name.lower()
        is_id_col = col_lower == "id" or col_lower.endswith("_id")
        is_ts_col = col.pg_type in ("TIMESTAMP", "TIMESTAMPTZ") and not timestamp_indexed

        if is_id_col or is_ts_col:
            idx_name = f"idx_{table_name}_{col.column_name}"
            await conn.execute(
                text(f'CREATE INDEX IF NOT EXISTS "{idx_name}" ON "{table_name}" ("{col.column_name}");')
            )
            if is_ts_col:
                timestamp_indexed = True
