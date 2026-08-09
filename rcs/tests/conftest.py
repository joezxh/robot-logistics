"""Pytest fixtures for RCS-1 tests.

RCS-1 is fully isolated: the registry is reset to a small default fixture
between unit tests. Integration tests use FastAPI TestClient with the
rcs_router mounted on a throwaway app (not backend.main).
"""
from __future__ import annotations
import pytest


@pytest.fixture
def reset_registry():
    from rcs import registry
    registry._reset_for_tests()
    yield
    registry._reset_for_tests()
