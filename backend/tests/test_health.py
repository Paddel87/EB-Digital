"""Tests for the /health endpoint."""

from __future__ import annotations

from fastapi.testclient import TestClient

from eb_digital import __version__
from eb_digital.app import create_app


def test_health_returns_ok_status_and_version() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": __version__}


def test_health_responds_with_json_content_type() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/health")
    assert response.headers["content-type"].startswith("application/json")
