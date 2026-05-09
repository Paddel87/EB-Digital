"""Tests for structured JSON logging and PII redaction."""

from __future__ import annotations

import json
import logging
from io import StringIO

import pytest

from eb_digital.logging import (
    REDACTED_VALUE,
    JsonLogFormatter,
    configure_logging,
    get_logger,
)


def _read_record(stream: StringIO) -> dict[str, object]:
    raw = stream.getvalue().strip()
    assert raw, "expected at least one log line"
    line = raw.splitlines()[-1]
    return json.loads(line)


def _attach_capture_handler(stream: StringIO) -> logging.Handler:
    handler = logging.StreamHandler(stream=stream)
    handler.setFormatter(JsonLogFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG)
    return handler


def test_log_output_is_one_json_object_per_line() -> None:
    stream = StringIO()
    _attach_capture_handler(stream)
    get_logger("test").info("hello world")
    record = _read_record(stream)
    assert record["message"] == "hello world"
    assert record["level"] == "INFO"
    assert record["logger"] == "test"
    assert "ts" in record


def test_password_field_in_extras_is_redacted() -> None:
    stream = StringIO()
    _attach_capture_handler(stream)
    get_logger("test").info("login_attempt", extra={"password": "hunter2", "username": "alice"})
    record = _read_record(stream)
    assert record["password"] == REDACTED_VALUE
    assert record["username"] == "alice"


@pytest.mark.parametrize(
    "field",
    [
        "password_hash",
        "access_code",
        "access_code_hash",
        "secret_key",
        "tomtom_api_key",
        "maptiler_api_key",
        "email",
        "coordinate_lat",
        "coordinate_lng",
    ],
)
def test_each_sensitive_field_is_redacted(field: str) -> None:
    stream = StringIO()
    _attach_capture_handler(stream)
    get_logger("test").info("event", extra={field: "should-not-appear"})
    record = _read_record(stream)
    assert record[field] == REDACTED_VALUE


def test_nested_redaction_through_dicts_and_lists() -> None:
    stream = StringIO()
    _attach_capture_handler(stream)
    get_logger("test").info(
        "nested",
        extra={
            "data": {"password": "leak", "ok": "fine"},
            "items": [{"email": "leak@example.com"}, {"label": "fine"}],
        },
    )
    record = _read_record(stream)
    data = record["data"]
    items = record["items"]
    assert isinstance(data, dict)
    assert isinstance(items, list)
    assert data["password"] == REDACTED_VALUE
    assert data["ok"] == "fine"
    assert items[0]["email"] == REDACTED_VALUE
    assert items[1]["label"] == "fine"


def test_configure_logging_replaces_existing_handlers() -> None:
    root = logging.getLogger()
    placeholder = logging.NullHandler()
    root.addHandler(placeholder)
    configure_logging("INFO")
    assert placeholder not in root.handlers
    assert len(root.handlers) == 1
    assert root.level == logging.INFO


def test_exception_info_is_serialized() -> None:
    stream = StringIO()
    _attach_capture_handler(stream)
    try:
        msg = "boom"
        raise RuntimeError(msg)
    except RuntimeError:
        get_logger("test").exception("error_occurred")
    record = _read_record(stream)
    assert "exc_info" in record
    exc_info = record["exc_info"]
    assert isinstance(exc_info, str)
    assert "RuntimeError" in exc_info
