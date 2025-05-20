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
    assert "Invalid markdown format" in response.json()["detail"]