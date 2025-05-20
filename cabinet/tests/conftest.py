"""Test configuration for Catalyzer::Cabinet."""

import pytest
import duckdb
from fastapi.testclient import TestClient

from cabinet.main import app
from cabinet.database import CabinetDB


@pytest.fixture
def test_db():
    """Create a temporary test database."""
    # Use an in-memory database for testing
    conn = duckdb.connect(":memory:")
    
    # Create the test table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS cabinet (
        id UUID PRIMARY KEY,
        title VARCHAR,
        author VARCHAR,
        url VARCHAR,
        tags VARCHAR[],
        locations VARCHAR[],
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        content VARCHAR
    )
    """)
    
    yield conn
    conn.close()


@pytest.fixture
def client(test_db):
    """Get a test client for the FastAPI app with a clean database."""
    # Create a test client with the connection
    return TestClient(app)