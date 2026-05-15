"""
query.py
--------
POST /query — full NL→SQL pipeline:
  prompt → schema context → Groq LLM → sqlglot safety → Redis cache → execute → log
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.postgres import get_db
from app.models.dataset import Dataset
from app.models.column_metadata import ColumnMetadata
from app.models.query_log import QueryLog
from app.schemas.query import QueryRequest, QueryMetadata, QueryResponse
from app.llm.sql_generator import generate_sql
from app.services.sql_safety import validate_sql
from app.services.query_executor import execute_query
from app.services.cache import get_cached_result, set_cached_result

router = APIRouter(prefix="/query", tags=["Query"])


@router.post("", response_model=QueryResponse)
async def run_query(
    body: QueryRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Convert a natural language prompt to SQL and execute it against the dataset.
    """
    # --- 1. Load dataset ---
    dataset = await db.get(Dataset, body.dataset_id)
    if dataset is None:
        raise HTTPException(
            status_code=404,
            detail=f"Dataset with id={body.dataset_id} not found.",
        )

    # --- 2. Load column metadata ---
    col_result = await db.execute(
        select(ColumnMetadata)
        .where(ColumnMetadata.dataset_id == body.dataset_id)
        .order_by(ColumnMetadata.ordinal_position)
    )
    columns = col_result.scalars().all()

    if not columns:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Dataset '{dataset.name}' (id={body.dataset_id}) has no column metadata. "
                "The ingestion pipeline may have failed to persist column info."
            ),
        )

    # --- 3. Check Redis cache ---
    cache_hit = False
    cached = await get_cached_result(body.dataset_id, body.prompt)

    if cached:
        cache_hit = True
        col_names, rows = cached
        execution_ms = 0
        sql = "(served from cache)"
    else:
        # --- 4. Generate SQL via LLM ---
        try:
            sql = await generate_sql(dataset, list(columns), body.prompt)
        except RuntimeError as exc:
            await _log_query(db, body.dataset_id, body.prompt, None, "llm_error", 0, 0, False, str(exc))
            raise HTTPException(status_code=502, detail=f"LLM error: {exc}")

        # --- 5. Safety validation ---
        # validate_sql raises HTTPException directly on failure
        validate_sql(sql, dataset.table_name)

        # --- 6. Execute ---
        col_names, rows, execution_ms = await execute_query(db, sql)

        # --- 7. Cache result ---
        await set_cached_result(body.dataset_id, body.prompt, col_names, rows)

    # --- 8. Log query ---
    await _log_query(
        db, body.dataset_id, body.prompt, sql,
        "success", execution_ms, len(rows), cache_hit, None
    )

    return QueryResponse(
        success=True,
        columns=col_names,
        rows=rows,
        metadata=QueryMetadata(
            generated_sql=sql,
            execution_time_ms=execution_ms,
            result_row_count=len(rows),
            cache_hit=cache_hit,
            dataset_table=dataset.table_name,
        ),
    )


async def _log_query(
    db: AsyncSession,
    dataset_id: int,
    prompt: str,
    sql: str | None,
    status: str,
    execution_ms: int,
    row_count: int,
    cache_hit: bool,
    error_message: str | None,
) -> None:
    log = QueryLog(
        dataset_id=dataset_id,
        prompt=prompt,
        generated_sql=sql,
        status=status,
        execution_time_ms=execution_ms,
        result_row_count=row_count,
        cache_hit=cache_hit,
        error_message=error_message,
    )
    db.add(log)
    await db.commit()
