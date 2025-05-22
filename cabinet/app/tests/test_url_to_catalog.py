"""Tests for URL to catalog conversion API."""

from unittest.mock import patch
from fastapi.testclient import TestClient

from cabinet.app.main import app


def test_create_catalog_from_url():
    """Test the endpoint for creating catalog from URL."""
    client = TestClient(app)
    
    # Mock the markdown service
    markdown_content = """---
title: URL Generated Catalog
author: url@example.com
url: https://example.com/test-url
tags: [url, test]
locations: [https://example.com/test-url]
---
# URL Generated Content

This is content generated from a URL.
"""
    
    # Path the MarkdownService.convert_url_to_markdown method
    with patch('cabinet.app.services.markdown_service.MarkdownService.convert_url_to_markdown') as mock_convert:
        mock_convert.return_value = markdown_content
        
        # Call the endpoint
        response = client.get("/org_name/group_name/user_name/new?url=https://example.com/test-url")
        
        # Check the response - we expect a 201 status code for successful creation
        assert response.status_code == 201
        
        # Verify the mock was called with the correct URL
        mock_convert.assert_called_once_with("https://example.com/test-url")