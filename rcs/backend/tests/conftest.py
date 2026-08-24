"""Test fixtures shared across rcs/backend tests."""
from __future__ import annotations
import pytest
from fastapi.testclient import TestClient
from rcs.main import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def client(app):
    return TestClient(app)
