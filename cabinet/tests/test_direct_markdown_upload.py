"""Tests for direct markdown content upload."""

import io
import pytest
from fastapi.testclient import TestClient

from cabinet.main import app


@pytest.fixture
def client():
    """Get a test client for the FastAPI app."""
    return TestClient(app)


def test_upload_direct_markdown_simple(client):
    """Test uploading a simple markdown content directly."""
    markdown_content = """---
title: Simple Direct Markdown
author: simple@example.com
url: https://example.com/simple
---
# Simple Content

This is a simple markdown file.
"""

    response = client.post(
        "/default/cabinet/new",
        content=markdown_content.encode("utf-8"),
        headers={"Content-Type": "text/markdown"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Simple Direct Markdown"
    assert data["markdown"].startswith("# Simple Content")