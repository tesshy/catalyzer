"""Tests for URL to markdown conversion endpoint."""

import pytest
import yaml
import re
import io
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from cabinet.main import app
from markitdown._base_converter import DocumentConverterResult


@pytest.fixture
def client():
    """Get a test client for the FastAPI app."""
    return TestClient(app)


def test_url_to_markdown_success(client):
    """Test successful conversion of URL to markdown."""
    with patch('markitdown.MarkItDown') as MockMarkItDown:
        # Set up the mock
        mock_instance = MockMarkItDown.return_value
        mock_instance.convert_url.return_value = DocumentConverterResult(
            markdown="# Test Title\n\nThis is test content.",
            title="Test Title"
        )
        
        # Call the endpoint
        response = client.get("/?url=https://example.com")
        
        # Check the response
        assert response.status_code == 200
        
        # Validate the content structure
        content = response.text
        
        # Check if it has front matter
        pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
        match = re.match(pattern, content, re.DOTALL)
        assert match is not None, "Response should contain frontmatter"
        
        frontmatter_str, main_content = match.groups()
        frontmatter = yaml.safe_load(frontmatter_str)
        
        # Validate front matter fields
        assert "title" in frontmatter
        assert frontmatter["title"] == "Test Title"
        assert "url" in frontmatter
        assert frontmatter["url"] == "https://example.com"
        assert "tags" in frontmatter
        assert isinstance(frontmatter["tags"], list)
        assert "locations" in frontmatter
        assert frontmatter["locations"] == ["https://example.com"]
        assert "created_at" in frontmatter
        assert "updated_at" in frontmatter
        
        # Validate markdown content
        assert "# Test Title" in main_content
        assert "This is test content." in main_content
        
        # Verify the mock was called
        mock_instance.convert_url.assert_called_once_with("https://example.com")


def test_url_to_markdown_error(client):
    """Test handling of errors during URL conversion."""
    with patch('markitdown.MarkItDown') as MockMarkItDown:
        # Set up the mock to raise an exception
        mock_instance = MockMarkItDown.return_value
        mock_instance.convert_url.side_effect = Exception("Failed to fetch URL")
        
        # Call the endpoint
        response = client.get("/?url=https://invalid-url.example")
        
        # Check the response
        assert response.status_code == 400
        assert "Failed to generate markdown from URL" in response.json()["detail"]
        
        # Verify the mock was called
        mock_instance.convert_url.assert_called_once_with("https://invalid-url.example")


def test_url_to_markdown_missing_parameter(client):
    """Test the endpoint when the URL parameter is missing."""
    response = client.get("/")
    
    # Check the response
    assert response.status_code == 422  # Validation error