"""
csv_loader.py
-------------
Loads a pandas DataFrame into a dynamic Postgres table in batched inserts.
Uses SQLAlchemy core (not ORM) for high-throughput row insertion.
"""
from __future__ import annotations

import pandas as pd
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from app.ingestion.schema_inference import InferredColumn

BATCH_SIZE = 10_000


async def load_dataframe(
    conn: AsyncConnection,
    df: pd.DataFrame,
    table_name: str,
    columns: list[InferredColumn],
) -> int:
    """
    Insert all rows from `df` into `table_name` in batches of BATCH_SIZE.

    Returns the number of rows inserted.

    Raises
    ------
    RuntimeError
        If insertion fails, with the original exception chained.
    """
    # Rename df columns to the sanitized names used during table creation
    rename_map = {
        orig: col.column_name
        for orig, col in zip(df.columns, columns)
    }
    df = df.rename(columns=rename_map)

    # Only keep columns that were successfully inferred
    col_names = [col.column_name for col in columns]
    df = df[col_names]

    # Replace NaN/NaT with None for Postgres NULL compatibility
    df = df.where(pd.notna(df), other=None)

    quoted_cols = ", ".join(f'"{c}"' for c in col_names)
    placeholders = ", ".join(f":{c}" for c in col_names)
    insert_sql = text(
        f'INSERT INTO "{table_name}" ({quoted_cols}) VALUES ({placeholders})'
    )

    total_rows = len(df)
    inserted = 0

    try:
        for start in range(0, total_rows, BATCH_SIZE):
            batch = df.iloc[start : start + BATCH_SIZE]
            records = batch.to_dict(orient="records")
            await conn.execute(insert_sql, records)
            inserted += len(records)
    except Exception as exc:
        raise RuntimeError(
            f"Failed to insert rows into '{table_name}' at batch starting row {inserted}. "
            f"Error: {exc}"
        ) from exc

    return inserted
