"""Tests for markdown file upload."""

import io
import pytest
from fastapi.testclient import TestClient

from cabinet.main import app


@pytest.fixture
def client():
    """Get a test client for the FastAPI app."""
    return TestClient(app)


def test_upload_markdown(client):
    """Test uploading a markdown file."""
    # Create a test markdown file
    markdown_content = """---
title: Test Markdown
author: test@example.com
url: https://example.com/test
tags: [test, markdown]
locations: [https://example.com/data1, https://example.com/data2]
created_at: 2023-01-01T00:00:00Z
updated_at: 2023-01-01T00:00:00Z
---
# Test Markdown

This is a test markdown file for testing the upload functionality.
"""

    # Create a file-like object
    file = io.BytesIO(markdown_content.encode("utf-8"))

    # Upload the file
    response = client.post(
        "/catalogs/new",
        files={"file": ("test.md", file, "text/markdown")},
    )

    # Check the response
    assert response.status_code == 201
    data = response.json()
    
    # Validate the returned data
    assert data["title"] == "Test Markdown"
    assert data["author"] == "test@example.com"
    assert data["url"] == "https://example.com/test"
    assert data["tags"] == ["test", "markdown"]
    assert data["locations"] == ["https://example.com/data1", "https://example.com/data2"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_upload_non_markdown_file(client):
    """Test uploading a non-markdown file."""
    # Create a test non-markdown file
    file_content = "This is not a markdown file."
    file = io.BytesIO(file_content.encode("utf-8"))

    # Upload the file
    response = client.post(
        "/catalogs/new",
        files={"file": ("test.txt", file, "text/plain")},
    )

    # Check the response
    assert response.status_code == 400
    assert "Only Markdown files are accepted" in response.json()["detail"]


def test_upload_invalid_markdown(client):
    """Test uploading an invalid markdown file (missing frontmatter)."""
    # Create an invalid markdown file
    markdown_content = """# No Frontmatter

This markdown file has no frontmatter.
"""
    file = io.BytesIO(markdown_content.encode("utf-8"))

    # Upload the file
    response = client.post(
        "/catalogs/new",
        files={"file": ("invalid.md", file, "text/markdown")},
    )

    # Check the response
    assert response.status_code == 400
    assert "Failed to parse markdown" in response.json()["detail"]