"""
datasets.py
-----------
GET /datasets        — list all datasets with summary metadata
GET /datasets/{id}   — full dataset info including column schema
"""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db
from app.models.dataset import Dataset
from app.models.column_metadata import ColumnMetadata
from app.schemas.upload import ColumnInfo, DatasetInfo

router = APIRouter(prefix="/datasets", tags=["Datasets"])


@router.get("", response_model=list[DatasetInfo])
async def list_datasets(db: AsyncSession = Depends(get_db)):
    """Return all uploaded datasets with their column schemas."""
    result = await db.execute(
        select(Dataset)
        .options(selectinload(Dataset.columns))
        .order_by(Dataset.created_at.desc())
    )
    datasets = result.scalars().all()
    return [_build_dataset_info(ds) for ds in datasets]


@router.get("/{dataset_id}", response_model=DatasetInfo)
async def get_dataset(dataset_id: int, db: AsyncSession = Depends(get_db)):
    """Return a single dataset with full column schema."""
    result = await db.execute(
        select(Dataset)
        .options(selectinload(Dataset.columns))
        .where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()

    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset with id={dataset_id} does not exist.",
        )

    return _build_dataset_info(dataset)


@router.delete("/{dataset_id}", status_code=204)
async def delete_dataset(dataset_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a dataset record and its associated metadata (does NOT drop the data table)."""
    dataset = await db.get(Dataset, dataset_id)
    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset with id={dataset_id} does not exist.",
        )
    await db.delete(dataset)
    await db.commit()


def _build_dataset_info(dataset: Dataset) -> DatasetInfo:
    col_infos = [
        ColumnInfo(
            column_name=col.column_name,
            pg_type=col.pg_type,
            pandas_dtype=col.pandas_dtype,
            is_nullable=col.is_nullable,
            sample_values=_parse_samples(col.sample_values),
            ordinal_position=col.ordinal_position,
        )
        for col in sorted(dataset.columns, key=lambda c: c.ordinal_position)
    ]

    return DatasetInfo(
        id=dataset.id,
        name=dataset.name,
        original_filename=dataset.original_filename,
        table_name=dataset.table_name,
        row_count=dataset.row_count,
        column_count=dataset.column_count,
        file_size_bytes=dataset.file_size_bytes,
        created_at=dataset.created_at.isoformat(),
        columns=col_infos,
    )


def _parse_samples(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return [raw]
