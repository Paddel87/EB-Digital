"""Tests for the PostgreSQL statement splitter used in the procrastinate
schema migration (Schritt 1.5).

The splitter is defined inside the migration module; we import it here via
its absolute path so mypy/ruff can resolve it without making the migration
file part of the application package.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_MIGRATION_PATH = (
    Path(__file__).resolve().parents[1]
    / "migrations"
    / "versions"
    / "20260509_1e343dae5fc4_add_procrastinate_schema.py"
)


def _load_split_function() -> object:
    spec = importlib.util.spec_from_file_location(
        "eb_digital_test_migration_1e343dae5fc4", _MIGRATION_PATH
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module._split_postgres_statements  # type: ignore[attr-defined]  # noqa: SLF001


_split = _load_split_function()


def test_splitter_handles_simple_statements() -> None:
    sql = "CREATE TABLE a (id int); CREATE TABLE b (id int);"
    parts = _split(sql)
    assert parts == ["CREATE TABLE a (id int)", "CREATE TABLE b (id int)"]


def test_splitter_ignores_trailing_whitespace_and_empty_chunks() -> None:
    sql = "  ; SELECT 1; ;\n"
    parts = _split(sql)
    assert parts == ["SELECT 1"]


def test_splitter_protects_dollar_quoted_function_body() -> None:
    sql = """
    CREATE FUNCTION foo() RETURNS void AS $$
    BEGIN
        PERFORM 1;
        PERFORM 2;
    END;
    $$ LANGUAGE plpgsql;

    SELECT 1;
    """
    parts = _split(sql)
    assert len(parts) == 2
    assert parts[0].startswith("CREATE FUNCTION foo()")
    assert "PERFORM 1;" in parts[0]
    assert "PERFORM 2;" in parts[0]
    assert parts[1] == "SELECT 1"


def test_splitter_protects_tagged_dollar_quote() -> None:
    sql = """
    DO $custom_tag$
    BEGIN
        RAISE NOTICE 'inner; semicolon should not split';
    END;
    $custom_tag$;

    SELECT 'after';
    """
    parts = _split(sql)
    assert len(parts) == 2
    assert "inner; semicolon should not split" in parts[0]
    assert parts[1] == "SELECT 'after'"


def test_splitter_handles_consecutive_dollar_blocks() -> None:
    sql = (
        "CREATE FUNCTION a() RETURNS void AS $$ BEGIN PERFORM 1; END; $$ LANGUAGE plpgsql;"
        " CREATE FUNCTION b() RETURNS void AS $$ BEGIN PERFORM 2; END; $$ LANGUAGE plpgsql;"
    )
    parts = _split(sql)
    assert len(parts) == 2
    assert parts[0].startswith("CREATE FUNCTION a()")
    assert parts[1].startswith("CREATE FUNCTION b()")


def test_splitter_returns_full_text_when_no_terminator() -> None:
    sql = "SELECT 1"
    assert _split(sql) == ["SELECT 1"]


@pytest.mark.parametrize(
    "sql",
    [
        "",
        "   \n\n  ",
        ";",
        "  ;  ",
    ],
)
def test_splitter_returns_empty_list_for_empty_or_whitespace_only_input(sql: str) -> None:
    assert _split(sql) == []


def test_splitter_keeps_invalid_dollar_tag_as_literal_text() -> None:
    # ``$abc!`` is not a valid dollar-quote tag (``!`` is not [a-zA-Z0-9_]),
    # so the splitter must NOT enter dollar-quote mode and the ``;`` after
    # the literal must terminate the statement.
    sql = "SELECT '$abc!def'; SELECT 'next';"
    parts = _split(sql)
    assert parts == ["SELECT '$abc!def'", "SELECT 'next'"]
