"""Tests for the catalogs API."""

from datetime import datetime
import uuid
from typing import Dict, Any

import pytest
from fastapi.testclient import TestClient

from cabinet.main import app

# We'll use the fixture from conftest.py


def test_create_catalog(client):
    """Test creating a catalog entry."""
    catalog_data = {
        "title": "Test Catalog",
        "author": "test@example.com",
        "url": "https://example.com/catalog",
        "tags": ["test", "example"],
        "locations": ["https://example.com/data"],
        "content": "This is a test catalog.",
    }
    
    response = client.post("/catalogs/", json=catalog_data)
    assert response.status_code == 201
    data = response.json()
    
    assert data["title"] == "Test Catalog"
    assert data["author"] == "test@example.com"
    assert data["url"] == "https://example.com/catalog"
    assert data["tags"] == ["test", "example"]
    assert data["locations"] == ["https://example.com/data"]
    assert data["content"] == "This is a test catalog."
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    
    return data


def test_get_catalog(client):
    """Test getting a catalog entry."""
    # First, create a catalog entry
    created = test_create_catalog(client)
    
    # Now get it
    response = client.get(f"/catalogs/{created['id']}")
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == created["id"]
    assert data["title"] == created["title"]


def test_update_catalog(client):
    """Test updating a catalog entry."""
    # First, create a catalog entry
    created = test_create_catalog(client)
    
    # Now update it
    update_data = {
        "title": "Updated Catalog",
        "tags": ["test", "updated"],
    }
    response = client.put(f"/catalogs/{created['id']}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == created["id"]
    assert data["title"] == "Updated Catalog"
    assert data["tags"] == ["test", "updated"]
    assert data["author"] == created["author"]  # Unchanged


def test_delete_catalog(client):
    """Test deleting a catalog entry."""
    # First, create a catalog entry
    created = test_create_catalog(client)
    
    # Now delete it
    response = client.delete(f"/catalogs/{created['id']}")
    assert response.status_code == 204
    
    # Verify it's gone
    response = client.get(f"/catalogs/{created['id']}")
    assert response.status_code == 404


def test_search_catalogs(client):
    """Test searching for catalogs."""
    # Create some catalog entries
    catalog1 = {
        "title": "Python Data",
        "author": "test1@example.com",
        "url": "https://example.com/catalog1",
        "tags": ["python", "data"],
        "locations": ["https://example.com/data1"],
        "content": "This is Python data.",
    }
    response1 = client.post("/catalogs/", json=catalog1)
    assert response1.status_code == 201
    
    catalog2 = {
        "title": "JavaScript Code",
        "author": "test2@example.com",
        "url": "https://example.com/catalog2",
        "tags": ["javascript", "code"],
        "locations": ["https://example.com/data2"],
        "content": "This is JavaScript code.",
    }
    response2 = client.post("/catalogs/", json=catalog2)
    assert response2.status_code == 201
    
    # Search by tag
    response = client.get("/catalogs/search/?tag=python")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1  # At least one result (there might be results from previous test runs)
    assert any(item["title"] == "Python Data" for item in data)
    
    # Search by query
    response = client.get("/catalogs/search/?q=JavaScript")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1  # At least one result (there might be results from previous test runs)
    assert any(item["title"] == "JavaScript Code" for item in data)
    
    # Search by both
    response = client.get("/catalogs/search/?tag=code&q=JavaScript")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1  # At least one result (there might be results from previous test runs)
    assert any(item["title"] == "JavaScript Code" for item in data)
    
    # Search with no results
    response = client.get("/catalogs/search/?tag=nonexistent-tag-that-does-not-exist")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


def test_search_catalogs_empty(client):
    """Test search with no parameters."""
    response = client.get("/catalogs/search/")
    assert response.status_code == 400