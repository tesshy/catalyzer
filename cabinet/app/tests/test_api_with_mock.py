from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import re
import yaml
from cabinet.main import app
from cabinet.services.markdown_service import get_markdown_service

# Create a test client
client = TestClient(app)

# パッチを作成
with patch('cabinet.services.markdown_service.get_markdown_service') as mock_get_service:
    # モックサービスを設定
    mock_service = MagicMock()
    mock_service.convert_url_to_markdown.return_value = """---
title: Example Mock Title
author: ''
url: https://example.com
tags: []
locations:
- https://example.com
created_at: '2023-10-10T12:00:00'
updated_at: '2023-10-10T12:00:00'
---

# Example Mock Title

This is mocked content from the mock service.
"""
    mock_get_service.return_value = mock_service
    
    # APIを呼び出してテスト
    response = client.get("/?url=https://example.com")
    print(f"Status code: {response.status_code}")
    print(f"Response content: {response.text[:100]}...")  # 最初の100文字だけ表示
    
    # モックが正しく呼ばれたことを確認
    mock_service.convert_url_to_markdown.assert_called_once_with("https://example.com")
    
    # フロントマターを確認
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, response.text, re.DOTALL)
    if match:
        frontmatter_str, content = match.groups()
        frontmatter = yaml.safe_load(frontmatter_str)
        print("\nFrontmatter:")
        for key, value in frontmatter.items():
            print(f"  {key}: {value}")
        
        print("\nContent (first 50 chars):")
        print(content[:50])
        
        print("\nTest passed!")
    else:
        print("No frontmatter found!")
        print("Test failed!")

