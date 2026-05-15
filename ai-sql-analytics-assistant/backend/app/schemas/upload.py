from __future__ import annotations
from pydantic import BaseModel


class ColumnInfo(BaseModel):
    column_name: str
    pg_type: str
    pandas_dtype: str
    is_nullable: bool
    sample_values: list[str]
    ordinal_position: int


class DatasetInfo(BaseModel):
    id: int
    name: str
    original_filename: str
    table_name: str
    row_count: int
    column_count: int
    file_size_bytes: int | None
    created_at: str
    columns: list[ColumnInfo] = []


class UploadResponse(BaseModel):
    success: bool
    message: str
    dataset: DatasetInfo
