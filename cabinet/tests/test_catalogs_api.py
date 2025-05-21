"""Tests for the catalogs API."""

from datetime import datetime
import uuid
from typing import Dict, Any

import pytest
from fastapi.testclient import TestClient

from cabinet.main import app


@pytest.fixture
def client():
    """Get a test client for the FastAPI app."""
    return TestClient(app)


def test_create_catalog(client):
    """Test creating a catalog entry."""
    catalog_data = {
        "title": "Test Catalog",
        "author": "test@example.com",
        "url": "https://example.com/catalog",
        "tags": ["test", "example"],
        "locations": ["https://example.com/data"],
        "markdown": "This is a test catalog.",
    }
    
    response = client.post("/default/cabinet/", json=catalog_data)
    assert response.status_code == 201
    data = response.json()
    
    assert data["title"] == "Test Catalog"
    assert data["author"] == "test@example.com"
    assert data["url"] == "https://example.com/catalog"
    assert data["tags"] == ["test", "example"]
    assert data["locations"] == ["https://example.com/data"]
    assert data["markdown"] == "This is a test catalog."
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data
    
    return data


def test_get_catalog(client):
    """Test getting a catalog entry."""
    # First, create a catalog entry
    created = test_create_catalog(client)
    
    # Now get it
    response = client.get(f"/default/cabinet/{created['id']}")
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
    response = client.put(f"/default/cabinet/{created['id']}", json=update_data)
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
    response = client.delete(f"/default/cabinet/{created['id']}")
    assert response.status_code == 204
    
    # Verify it's gone
    response = client.get(f"/default/cabinet/{created['id']}")
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
        "markdown": "This is Python data.",
    }
    response1 = client.post("/default/cabinet/", json=catalog1)
    assert response1.status_code == 201
    
    catalog2 = {
        "title": "JavaScript Code",
        "author": "test2@example.com",
        "url": "https://example.com/catalog2",
        "tags": ["javascript", "code"],
        "locations": ["https://example.com/data2"],
        "markdown": "This is JavaScript code.",
    }
    response2 = client.post("/default/cabinet/", json=catalog2)
    assert response2.status_code == 201
    
    # Search by tag
    response = client.get("/default/cabinet/search/?tag=python")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Python Data"
    
    # Search by query
    response = client.get("/default/cabinet/search/?q=JavaScript")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "JavaScript Code"
    
    # Search by both
    response = client.get("/default/cabinet/search/?tag=code&q=JavaScript")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "JavaScript Code"
    
    # Search with no results
    response = client.get("/default/cabinet/search/?tag=nonexistent")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0


def test_search_catalogs_empty(client):
    """Test search with no parameters."""
    response = client.get("/default/cabinet/search/")
    assert response.status_code == 400