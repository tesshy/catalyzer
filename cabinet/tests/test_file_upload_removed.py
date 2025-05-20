"""Tests to verify that file upload functionality has been removed."""

import io
import pytest
from fastapi.testclient import TestClient

from cabinet.main import app


@pytest.fixture
def client():
    """Get a test client for the FastAPI app."""
    return TestClient(app)


def test_file_upload_no_longer_supported(client):
    """Test that file upload is no longer supported and returns an error."""
    # Create a test markdown file
    markdown_content = """---
title: Test Upload
author: test@example.com
url: https://example.com/test
---
# Test Content

This is a test markdown file.
"""
    file = io.BytesIO(markdown_content.encode("utf-8"))

    # Attempt to upload the file
    response = client.post(
        "/catalogs/new",
        files={"file": ("test.md", file, "text/markdown")},
    )

    # Check the response - should now indicate that Content-Type must be text/markdown
    assert response.status_code == 400
    assert "Content-Type must be text/markdown" in response.json()["detail"]