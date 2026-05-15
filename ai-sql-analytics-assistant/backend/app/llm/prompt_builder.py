"""
prompt_builder.py
-----------------
Constructs the schema-aware system prompt injected into every LLM call.
The prompt explicitly constrains the model to the exact table and column names.
"""
from __future__ import annotations

import json
from app.models.dataset import Dataset
from app.models.column_metadata import ColumnMetadata


def build_system_prompt(dataset: Dataset, columns: list[ColumnMetadata]) -> str:
    """
    Build a strict system prompt that tells the LLM:
    - The exact table name to query
    - Every column name, its type, and sample values
    - Hard rules: SELECT only, no hallucinated column names
    """
    col_lines: list[str] = []
    for col in sorted(columns, key=lambda c: c.ordinal_position):
        samples = ""
        if col.sample_values:
            try:
                sample_list = json.loads(col.sample_values)
                samples = f" (samples: {', '.join(str(s) for s in sample_list[:3])})"
            except json.JSONDecodeError:
                samples = ""
        nullable_hint = " [nullable]" if col.is_nullable else " [NOT NULL]"
        col_lines.append(
            f'  - "{col.column_name}" ({col.pg_type}{nullable_hint}){samples}'
        )

    columns_block = "\n".join(col_lines)

    return f"""You are a precise SQL generation assistant for a PostgreSQL analytics platform called SchemaIQ.

## Your Task
Convert the user's natural language question into a single, valid PostgreSQL SELECT query.

## Dataset Context
- Dataset name: {dataset.name}
- Table name: "{dataset.table_name}"
- Total rows: {dataset.row_count:,}
- Columns ({dataset.column_count} total):
{columns_block}

## Strict Rules — you MUST follow every one of these:
1. Output ONLY the raw SQL query — no explanations, no markdown, no code fences.
2. Use ONLY the exact column names listed above — never invent or guess column names.
3. The query MUST target the table named "{dataset.table_name}" exactly.
4. Only write SELECT statements — never INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, or any DDL.
5. Do not use subqueries unless absolutely necessary for the answer.
6. Always include a LIMIT clause (max 1000 rows) unless the question asks for aggregates.
7. Use double-quotes around column names that contain special characters or reserved words.
8. If the question cannot be answered with the available columns, output exactly:
   SELECT 'The question cannot be answered with the available columns.' AS error_message;

## Output
Return only the SQL query string, nothing else."""


def build_user_message(prompt: str) -> str:
    return f"Question: {prompt}"
