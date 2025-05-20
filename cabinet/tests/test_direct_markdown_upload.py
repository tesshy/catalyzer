"""Tests for direct markdown content upload."""

import io
import pytest
from fastapi.testclient import TestClient

from cabinet.main import app


@pytest.fixture
def client():
    """Get a test client for the FastAPI app."""
    return TestClient(app)


def test_upload_direct_markdown(client):
    """Test uploading markdown content directly with content-type text/markdown."""
    # Create a valid markdown content
    markdown_content = """---
title: Direct Markdown
author: direct@example.com
url: https://example.com/direct
tags:
  - direct
  - markdown
locations:
  - https://example.com/direct-data
---
# Direct Markdown

This is markdown content sent directly with content-type text/markdown.
"""

    # Upload the content directly with text/markdown content-type
    response = client.post(
        "/catalogs/new",
        content=markdown_content.encode("utf-8"),
        headers={"Content-Type": "text/markdown"}
    )

    # Print debug information
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.text}")

    # Check the response
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["title"] == "Direct Markdown"
    assert data["author"] == "direct@example.com"
    assert data["tags"] == ["direct", "markdown"]
    assert data["content"].startswith("# Direct Markdown")