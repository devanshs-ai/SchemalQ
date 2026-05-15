from __future__ import annotations
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    prompt: str = Field(..., min_length=5, description="Natural language question about the dataset")
    dataset_id: int = Field(..., description="ID of the dataset to query")


class QueryMetadata(BaseModel):
    generated_sql: str
    execution_time_ms: int
    result_row_count: int
    cache_hit: bool
    dataset_table: str


class QueryResponse(BaseModel):
    success: bool
    columns: list[str]
    rows: list[dict]
    metadata: QueryMetadata
