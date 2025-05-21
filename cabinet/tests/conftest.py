"""Pytest configuration for Cabinet tests."""

import pytest
from fastapi.testclient import TestClient

from ..main import app
from ..database import DB_CONNECTION, create_table


@pytest.fixture
def client():
    """Get a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def test_group():
    """Test group name."""
    return "test_group"


@pytest.fixture
def test_user():
    """Test user name."""
    return "test_user"


@pytest.fixture(autouse=True)
def setup_teardown_database(test_group, test_user):
    """Set up and clean up the database for each test."""
    # Create test table
    create_table(DB_CONNECTION, test_group, test_user)
    
    yield
    
    # Clean up the database after each test
    try:
        DB_CONNECTION.execute(f"DROP TABLE IF EXISTS {test_group}.{test_user}")
    except:
        pass  # Ignore errors if the table doesn't exist