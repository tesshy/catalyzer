"""Tests for the catalog service."""

import os
import uuid
from datetime import datetime
from unittest import TestCase

import duckdb
import pytest
from fastapi import Depends

from cabinet.database import CabinetDB
from cabinet.models import CatalogCreate, CatalogUpdate
from cabinet.services.catalog_service import CatalogService


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
def db(test_db):
    """Create a CabinetDB instance with the test database."""
    return CabinetDB(test_db)


@pytest.fixture
def service(db):
    """Create a CatalogService instance with the test database."""
    return CatalogService(db)


def test_create_catalog(service):
    """Test creating a catalog entry."""
    catalog = CatalogCreate(
        title="Test Catalog",
        author="test@example.com",
        url="https://example.com/catalog",
        tags=["test", "example"],
        locations=["https://example.com/data"],
        content="This is a test catalog.",
    )
    
    result = service.create_catalog(catalog)
    
    assert result.title == "Test Catalog"
    assert result.author == "test@example.com"
    assert str(result.url) == "https://example.com/catalog"
    assert result.tags == ["test", "example"]
    assert str(result.locations[0]) == "https://example.com/data"
    assert result.content == "This is a test catalog."
    assert result.id is not None
    assert result.created_at is not None
    assert result.updated_at is not None


def test_get_catalog(service):
    """Test getting a catalog entry."""
    # First, create a catalog entry
    catalog = CatalogCreate(
        title="Test Catalog",
        author="test@example.com",
        url="https://example.com/catalog",
        tags=["test", "example"],
        locations=["https://example.com/data"],
        content="This is a test catalog.",
    )
    created = service.create_catalog(catalog)
    
    # Now get it
    result = service.get_catalog(created.id)
    
    assert result is not None
    assert result.id == created.id
    assert result.title == "Test Catalog"


def test_update_catalog(service):
    """Test updating a catalog entry."""
    # First, create a catalog entry
    catalog = CatalogCreate(
        title="Test Catalog",
        author="test@example.com",
        url="https://example.com/catalog",
        tags=["test", "example"],
        locations=["https://example.com/data"],
        content="This is a test catalog.",
    )
    created = service.create_catalog(catalog)
    
    # Now update it
    update = CatalogUpdate(
        title="Updated Catalog",
        tags=["test", "updated"],
    )
    result = service.update_catalog(created.id, update)
    
    assert result is not None
    assert result.id == created.id
    assert result.title == "Updated Catalog"
    assert result.tags == ["test", "updated"]
    assert result.author == "test@example.com"  # Unchanged
    assert str(result.url) == "https://example.com/catalog"  # Unchanged


def test_delete_catalog(service):
    """Test deleting a catalog entry."""
    # First, create a catalog entry
    catalog = CatalogCreate(
        title="Test Catalog",
        author="test@example.com",
        url="https://example.com/catalog",
        tags=["test", "example"],
        locations=["https://example.com/data"],
        content="This is a test catalog.",
    )
    created = service.create_catalog(catalog)
    
    # Now delete it
    result = service.delete_catalog(created.id)
    assert result is True
    
    # Verify it's gone
    assert service.get_catalog(created.id) is None


def test_search_catalogs(service):
    """Test searching for catalogs."""
    # Create some catalog entries
    catalog1 = CatalogCreate(
        title="Python Data",
        author="test1@example.com",
        url="https://example.com/catalog1",
        tags=["python", "data"],
        locations=["https://example.com/data1"],
        content="This is Python data.",
    )
    service.create_catalog(catalog1)
    
    catalog2 = CatalogCreate(
        title="JavaScript Code",
        author="test2@example.com",
        url="https://example.com/catalog2",
        tags=["javascript", "code"],
        locations=["https://example.com/data2"],
        content="This is JavaScript code.",
    )
    service.create_catalog(catalog2)
    
    # Search by tag
    results = service.search_catalogs(tags=["python"])
    assert len(results) == 1
    assert results[0].title == "Python Data"
    
    # Search by query
    results = service.search_catalogs(query="JavaScript")
    assert len(results) == 1
    assert results[0].title == "JavaScript Code"
    
    # Search by both
    results = service.search_catalogs(tags=["code"], query="JavaScript")
    assert len(results) == 1
    assert results[0].title == "JavaScript Code"
    
    # Search with no results
    results = service.search_catalogs(tags=["nonexistent"])
    assert len(results) == 0