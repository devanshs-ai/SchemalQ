"""
sql_safety.py
-------------
AST-based SQL safety validator using sqlglot.
Blocks any statement that is not a pure SELECT.
No regex — sqlglot parses the full SQL grammar.
"""
from __future__ import annotations

import sqlglot
import sqlglot.expressions as exp
from fastapi import HTTPException


# Statements that are never allowed
_BLOCKED_STATEMENT_TYPES = (
    exp.Drop,
    exp.Delete,
    exp.Update,
    exp.Insert,
    exp.Create,
    exp.Alter,          # was AlterTable in older sqlglot versions
    exp.Command,        # Catches raw COPY, VACUUM, etc.
    exp.Transaction,
    exp.Rollback,
    exp.Commit,
    exp.Grant,
)


def validate_sql(sql: str, allowed_table: str) -> str:
    """
    Parse and validate a SQL string.

    Rules:
    1. Must be a single SELECT statement.
    2. Must not reference any table other than `allowed_table`.
    3. Must not contain any blocked statement types.

    Returns the original `sql` string if valid.

    Raises
    ------
    HTTPException(400)
        With a clear reason string if validation fails.
    """
    try:
        statements = sqlglot.parse(sql, dialect="postgres")
    except sqlglot.errors.ParseError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"SQL parse error: {exc}. Submitted SQL: {sql!r}",
        )

    if not statements:
        raise HTTPException(
            status_code=400,
            detail="No SQL statement was generated. The LLM returned an empty query.",
        )

    if len(statements) > 1:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Only single SELECT statements are allowed. "
                f"The LLM generated {len(statements)} statements."
            ),
        )

    statement = statements[0]

    # Check for blocked statement types
    for blocked_type in _BLOCKED_STATEMENT_TYPES:
        if isinstance(statement, blocked_type):
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Destructive or administrative SQL is not allowed. "
                    f"Statement type detected: {type(statement).__name__}. "
                    f"Only SELECT statements are permitted."
                ),
            )

    if not isinstance(statement, exp.Select):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Only SELECT statements are allowed. "
                f"The generated statement type is: {type(statement).__name__}."
            ),
        )

    # Validate that only the allowed table is referenced
    referenced_tables = {
        tbl.name.lower()
        for tbl in statement.find_all(exp.Table)
        if tbl.name
    }

    disallowed = referenced_tables - {allowed_table.lower()}
    if disallowed:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Query references unauthorized table(s): {disallowed}. "
                f"Only '{allowed_table}' is accessible for this dataset."
            ),
        )

    return sql
