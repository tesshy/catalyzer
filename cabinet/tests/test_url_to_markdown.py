"""Tests for URL to Markdown conversion."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from markitdown._base_converter import DocumentConverterResult

from ..main import app


@pytest.fixture
def client():
    """Get a test client for the FastAPI app."""
    return TestClient(app)


@patch("markitdown.MarkItDown.convert_url")
def test_url_to_markdown_conversion_success(mock_convert_url, client):
    """Test successful URL to Markdown conversion and catalog creation."""
    # モックの設定
    mock_result = DocumentConverterResult(
        markdown="# Test Content\nThis is a test markdown content.",
        title="Test Title"
    )
    mock_convert_url.return_value = mock_result
    
    # テスト用のURL
    test_url = "https://example.com/test"
    
    # APIエンドポイントのテスト
    response = client.get(f"/from_url?url={test_url}")
    
    # 結果の検証
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Title"
    assert "Test Content" in data["markdown"]
    assert data["url"] == "https://example.com/test"
    
    # markitdownのconvert_url関数が呼ばれたことを確認
    mock_convert_url.assert_called_once_with(test_url)


@patch("markitdown.MarkItDown.convert_url")
def test_url_to_markdown_conversion_failure(mock_convert_url, client):
    """Test URL to Markdown conversion failure."""
    # 例外を投げるようにモックを設定
    mock_convert_url.side_effect = Exception("Failed to convert URL")
    
    # テスト用のURL
    test_url = "https://invalid-url.example"
    
    # APIエンドポイントのテスト
    response = client.get(f"/from_url?url={test_url}")
    
    # 結果の検証
    assert response.status_code == 400
    assert "Failed to create catalog from URL" in response.json()["detail"]


def test_root_endpoint_with_url_param(client):
    """Test root endpoint with URL parameter redirection."""
    # URLパラメータ付きルートエンドポイントへのリクエスト
    test_url = "https://example.com/test"
    response = client.get(f"/?url={test_url}", allow_redirects=False)
    
    # リダイレクトの確認
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == f"/from_url?url={test_url}"


def test_root_endpoint_without_url_param(client):
    """Test root endpoint without URL parameter."""
    # URLパラメータなしのルートエンドポイント
    response = client.get("/")
    
    # 通常のレスポンスの確認
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Catalyzer::Cabinet"}