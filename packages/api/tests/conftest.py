"""Shared fixtures for API route tests."""

import pytest
from fastapi.testclient import TestClient

from narratological_api.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI app."""
    return TestClient(app)
