"""Tests for URL to markdown API endpoint."""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from markitdown._base_converter import DocumentConverterResult

from cabinet.main import app
from cabinet.services.markdown_service import MarkdownService


@pytest.fixture
def client():
    """Get a test client for the FastAPI app."""
    return TestClient(app)


def test_generate_markdown_from_url(client):
    """Test the endpoint for generating markdown from URL."""
    # パッチを当てる対象を正確に指定
    with patch.object(MarkdownService, "convert_url_to_markdown") as mock_convert:
        # モックの戻り値を設定
        mock_convert.return_value = "---\ntitle: Test\n---\n\n# Test Content"
        
        # エンドポイントを呼び出す
        response = client.get("/?url=https://example.com")
        
        # レスポンスを検証
        assert response.status_code == 200
        assert response.text == "---\ntitle: Test\n---\n\n# Test Content"
        
        # モックが正しく呼ばれたことを確認
        mock_convert.assert_called_once_with("https://example.com")