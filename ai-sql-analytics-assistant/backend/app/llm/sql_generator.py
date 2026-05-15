"""
sql_generator.py
----------------
Calls the Groq LLM and extracts the SQL string from the response.
Strips markdown code fences if the model adds them despite instructions.
"""
from __future__ import annotations

import re

from app.llm.groq_client import chat_completion
from app.llm.prompt_builder import build_system_prompt, build_user_message
from app.models.dataset import Dataset
from app.models.column_metadata import ColumnMetadata


async def generate_sql(
    dataset: Dataset,
    columns: list[ColumnMetadata],
    prompt: str,
) -> str:
    """
    Generate a SQL query from a natural language prompt.

    Returns the extracted SQL string.

    Raises
    ------
    RuntimeError
        If the LLM response is empty or cannot be parsed into SQL.
    """
    system_prompt = build_system_prompt(dataset, columns)
    user_message = build_user_message(prompt)

    raw_response = await chat_completion(
        system_prompt=system_prompt,
        user_message=user_message,
        temperature=0.1,
        max_tokens=512,
    )

    sql = _extract_sql(raw_response)

    if not sql:
        raise RuntimeError(
            f"LLM returned a response but no SQL could be extracted. "
            f"Raw response was: {raw_response!r}"
        )

    return sql


def _extract_sql(text: str) -> str:
    """
    Extract SQL from an LLM response.
    Handles markdown code fences (```sql ... ``` or ``` ... ```).
    """
    # Strip markdown code fences
    fenced = re.search(r"```(?:sql)?\s*([\s\S]+?)```", text, re.IGNORECASE)
    if fenced:
        return fenced.group(1).strip()

    # Strip single backtick inline code
    inline = re.search(r"`([^`]+)`", text)
    if inline:
        return inline.group(1).strip()

    return text.strip()
