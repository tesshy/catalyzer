"""Tests for direct markdown content upload."""

import io
import pytest
from fastapi.testclient import TestClient

from cabinet.main import app


def test_upload_direct_markdown_simple(client, test_group, test_user):
    """Test uploading a simple markdown content directly."""
    # Create a simple markdown file with minimal frontmatter
    markdown_content = """---
title: Simple Direct Markdown
author: simple@example.com
url: https://example.com/simple
---
# Simple Content

This is a simple markdown file.
"""

    # Upload the content directly with text/markdown content-type
    response = client.post(
        f"/{test_group}/{test_user}/new",
        content=markdown_content.encode("utf-8"),
        headers={"Content-Type": "text/markdown"}
    )

    # Check the response
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["title"] == "Simple Direct Markdown"
    assert data["author"] == "simple@example.com"
    assert data["markdown"].startswith("# Simple Content")
    
    # Check that the properties field contains the frontmatter data
    assert "properties" in data
    assert isinstance(data["properties"], dict)
    assert "title" in data["properties"]
    assert data["properties"]["title"] == "Simple Direct Markdown"