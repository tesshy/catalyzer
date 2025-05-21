"""Pytest configuration for Cabinet tests."""

import pytest
from fastapi.testclient import TestClient

from ..main import app


@pytest.fixture
def client():
    """Get a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def cleanup_database():
    """Clean up the database after each test."""
    from ..database import DB_CONNECTION
    
    yield
    
    # Clean up the database after each test
    DB_CONNECTION.execute("DELETE FROM cabinet")