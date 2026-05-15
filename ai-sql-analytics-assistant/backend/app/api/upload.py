"""
upload.py
---------
POST /upload — receives a CSV file, runs the full ingestion pipeline,
persists Dataset + ColumnMetadata records, and returns enriched schema info.
"""
from __future__ import annotations

import io
import json

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db, engine
from app.ingestion.schema_inference import infer_schema
from app.ingestion.table_manager import (
    _build_table_name,
    create_dataset_table,
    get_existing_table_names,
)
from app.ingestion.csv_loader import load_dataframe
from app.models.dataset import Dataset
from app.models.column_metadata import ColumnMetadata
from app.schemas.upload import ColumnInfo, DatasetInfo, UploadResponse

router = APIRouter(prefix="/upload", tags=["Upload"])

_ALLOWED_CONTENT_TYPES = {"text/csv", "application/csv", "text/plain", "application/octet-stream"}
_MAX_FILE_SIZE_BYTES = 500 * 1024 * 1024  # 500 MB


@router.post("", response_model=UploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a CSV file and ingest it into PostgreSQL.

    Returns the inferred schema, row count, and dataset ID.
    """
    # --- 1. Basic file validation ---
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail=f"Only .csv files are accepted. Received: '{file.filename}'",
        )

    raw_bytes = await file.read()
    file_size = len(raw_bytes)

    if file_size == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if file_size > _MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=(
                f"File exceeds the 500 MB limit. "
                f"Received: {file_size / 1024 / 1024:.1f} MB"
            ),
        )

    # --- 2. Parse CSV ---
    try:
        df = pd.read_csv(io.BytesIO(raw_bytes))
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Could not parse CSV file '{file.filename}': {exc}",
        )

    if df.empty:
        raise HTTPException(
            status_code=422,
            detail="CSV file was parsed but contains no data rows.",
        )

    if len(df.columns) == 0:
        raise HTTPException(status_code=422, detail="CSV file has no columns.")

    # --- 3. Infer schema ---
    try:
        inferred_columns = infer_schema(df)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    # --- 4. Determine unique table name ---
    async with engine.begin() as conn:
        existing_names = await get_existing_table_names(conn)

    dataset_name = file.filename.rsplit(".", 1)[0]
    table_name = _build_table_name(file.filename, existing_names)

    # --- 5. Create table + load data ---
    async with engine.begin() as conn:
        await create_dataset_table(conn, table_name, inferred_columns)
        rows_inserted = await load_dataframe(conn, df, table_name, inferred_columns)

    # --- 6. Persist metadata ---
    dataset = Dataset(
        name=dataset_name,
        original_filename=file.filename,
        table_name=table_name,
        row_count=rows_inserted,
        column_count=len(inferred_columns),
        file_size_bytes=file_size,
    )
    db.add(dataset)
    await db.flush()  # get the auto-generated id

    for col in inferred_columns:
        col_meta = ColumnMetadata(
            dataset_id=dataset.id,
            column_name=col.column_name,
            pg_type=col.pg_type,
            pandas_dtype=col.pandas_dtype,
            is_nullable=col.is_nullable,
            sample_values=json.dumps(col.sample_values),
            ordinal_position=col.ordinal_position,
        )
        db.add(col_meta)

    await db.commit()
    await db.refresh(dataset)

    # --- 7. Build response ---
    col_infos = [
        ColumnInfo(
            column_name=col.column_name,
            pg_type=col.pg_type,
            pandas_dtype=col.pandas_dtype,
            is_nullable=col.is_nullable,
            sample_values=col.sample_values,
            ordinal_position=col.ordinal_position,
        )
        for col in inferred_columns
    ]

    return UploadResponse(
        success=True,
        message=f"Successfully ingested {rows_inserted:,} rows from '{file.filename}'.",
        dataset=DatasetInfo(
            id=dataset.id,
            name=dataset.name,
            original_filename=dataset.original_filename,
            table_name=dataset.table_name,
            row_count=dataset.row_count,
            column_count=dataset.column_count,
            file_size_bytes=dataset.file_size_bytes,
            created_at=dataset.created_at.isoformat(),
            columns=col_infos,
        ),
    )