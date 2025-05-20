"""Pytest configuration for Cabinet tests."""

import pytest
import duckdb
from cabinet.database import create_table


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Set up and tear down a test database for all tests."""
    # Use an in-memory database for testing
    conn = duckdb.connect(":memory:")
    
    # Create the test table
    create_table(conn)
    
    yield conn
    
    conn.close()