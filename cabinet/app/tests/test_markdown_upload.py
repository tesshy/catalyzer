"""Tests for markdown file upload."""

import io
import pytest
import yaml
import re
from fastapi.testclient import TestClient

from cabinet.main import app


@pytest.fixture
def client():
    """Get a test client for the FastAPI app."""
    return TestClient(app)


def test_markdown_parsing():
    """Test parsing markdown frontmatter."""
    # Create a simple test markdown file
    markdown_content = """---
title: Test Markdown
author: test@example.com
url: https://example.com/test
---
# Test Markdown

This is a test markdown file for testing the upload functionality.
"""

    # Extract YAML frontmatter using regex
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, markdown_content, re.DOTALL)
    
    assert match is not None
    frontmatter_str, main_content = match.groups()
    
    # Parse YAML frontmatter
    frontmatter = yaml.safe_load(frontmatter_str)
    
    # Verify the parsed data
    assert frontmatter["title"] == "Test Markdown"
    assert frontmatter["author"] == "test@example.com"
    assert frontmatter["url"] == "https://example.com/test"
    assert main_content.startswith("# Test Markdown")


def test_non_markdown_content_type(client):
    """Test uploading with non-markdown content type."""
    # Try uploading with incorrect content-type
    response = client.post(
        "/catalogs/new",
        content="Some plain text",
        headers={"Content-Type": "text/plain"}
    )

    # Check the response
    assert response.status_code == 400
    assert "Content-Type must be text/markdown" in response.json()["detail"]


def test_upload_direct_markdown(client):
    """Test uploading markdown content directly with content-type text/markdown."""
    # Create a valid markdown content
    markdown_content = """---
title: Direct Upload
author: direct@example.com
url: https://example.com/direct
tags: [direct, test]
---
# Direct Upload

This is markdown content sent directly via text/markdown.
"""

    # Upload the content directly with text/markdown content-type
    response = client.post(
        "/catalogs/new",
        content=markdown_content.encode("utf-8"),
        headers={"Content-Type": "text/markdown"}
    )

    # Check the response
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Direct Upload"
    assert data["author"] == "direct@example.com"
    assert data["tags"] == ["direct", "test"]
    assert data["content"].startswith("# Direct Upload")
    assert "properties" in data
    # The properties field should contain the frontmatter
    assert isinstance(data["properties"], dict)


def test_upload_invalid_direct_markdown(client):
    """Test uploading invalid markdown content directly with missing frontmatter."""
    # Create an invalid markdown content
    markdown_content = """# No Frontmatter

This markdown content has no frontmatter and is sent directly.
"""

    # Upload the content directly with text/markdown content-type
    response = client.post(
        "/catalogs/new",
        content=markdown_content.encode("utf-8"),
        headers={"Content-Type": "text/markdown"}
    )

    # Check the response
    assert response.status_code == 400
    assert "Invalid markdown format" in response.json()["detail"]