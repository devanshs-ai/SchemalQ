"""
schema_inference.py
-------------------
Infers PostgreSQL column types and metadata from a pandas DataFrame.
No silent fallbacks — raises ValueError if a dtype cannot be mapped.
"""
from __future__ import annotations

import json
import pandas as pd
from dataclasses import dataclass


# Exhaustive dtype → PostgreSQL type mapping.
# Intentionally strict: unmapped dtypes raise ValueError so we notice immediately.
_DTYPE_TO_PG: dict[str, str] = {
    "int8": "SMALLINT",
    "int16": "SMALLINT",
    "int32": "INTEGER",
    "int64": "BIGINT",
    "uint8": "SMALLINT",
    "uint16": "INTEGER",
    "uint32": "BIGINT",
    "uint64": "BIGINT",
    "float32": "REAL",
    "float64": "DOUBLE PRECISION",
    "bool": "BOOLEAN",
    "object": "TEXT",
    "string": "TEXT",
    "datetime64[ns]": "TIMESTAMP",
    "datetime64[us]": "TIMESTAMP",
    "datetime64[ns, UTC]": "TIMESTAMPTZ",
    "datetime64[us, UTC]": "TIMESTAMPTZ",
    "date": "DATE",
    "category": "TEXT",
}


@dataclass
class InferredColumn:
    column_name: str
    pg_type: str
    pandas_dtype: str
    is_nullable: bool
    sample_values: list[str]
    ordinal_position: int


def infer_schema(df: pd.DataFrame) -> list[InferredColumn]:
    """
    Infer PostgreSQL column types from a DataFrame.

    Raises
    ------
    ValueError
        If any column has a dtype that cannot be mapped to a Postgres type.
    """
    result: list[InferredColumn] = []

    for position, col in enumerate(df.columns):
        series = df[col]
        dtype_str = str(series.dtype)

        pg_type = _DTYPE_TO_PG.get(dtype_str)

        # Try converting object columns that look like datetimes
        if pg_type is None and dtype_str == "object":
            try:
                pd.to_datetime(series.dropna().head(10), infer_datetime_format=True)
                pg_type = "TIMESTAMP"
                dtype_str = "object(datetime-like)"
            except Exception:
                pass

        if pg_type is None:
            raise ValueError(
                f"Column '{col}' has dtype '{dtype_str}' which cannot be mapped to a "
                f"PostgreSQL type. Supported dtypes: {sorted(_DTYPE_TO_PG.keys())}"
            )

        is_nullable = bool(series.isnull().any())

        # Extract up to 5 non-null sample values, coerced to strings
        samples = (
            series.dropna()
            .head(5)
            .astype(str)
            .tolist()
        )

        result.append(
            InferredColumn(
                column_name=_sanitize_column_name(col),
                pg_type=pg_type,
                pandas_dtype=str(series.dtype),
                is_nullable=is_nullable,
                sample_values=samples,
                ordinal_position=position,
            )
        )

    return result


def _sanitize_column_name(name: str) -> str:
    """
    Convert a column name to a valid, lowercase PostgreSQL identifier.
    Replaces spaces and special characters with underscores.
    """
    import re
    sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", name.strip()).lower()
    # Prefix with underscore if it starts with a digit
    if sanitized and sanitized[0].isdigit():
        sanitized = f"col_{sanitized}"
    if not sanitized:
        raise ValueError(f"Column name '{name}' produces an empty identifier after sanitization.")
    return sanitized
