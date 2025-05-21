"""Pytest configuration for Cabinet tests."""

import pytest
import duckdb
from cabinet.database import create_table


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Set up and tear down a test database for all tests."""
    # Use an in-memory database for testing
    conn = duckdb.connect(":memory:")
    
    # Create the schema and test table
    conn.execute("CREATE SCHEMA IF NOT EXISTS \"default\"")
    conn.execute("SET search_path TO \"default\"")
    create_table(conn, "cabinet")
    
    yield conn
    
    conn.close()