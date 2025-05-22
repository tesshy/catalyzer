from fastapi.testclient import TestClient
from cabinet.main import app
import json
import re
import yaml
from unittest.mock import patch
from markitdown._base_converter import DocumentConverterResult

# Create a test client
client = TestClient(app)

# Configure the mock
with patch('markitdown.MarkItDown', autospec=True) as MockMarkItDown:
    # Create a mock instance and configure it
    mock_instance = MockMarkItDown.return_value
    mock_instance.convert_url.return_value = DocumentConverterResult(
        markdown="# Test Title\n\nThis is test content.",
        title="Test Title"
    )
    
    # Test the endpoint
    print("Testing URL to markdown endpoint...")
    response = client.get("/?url=https://example.com")
    print(f"Status Code: {response.status_code}")
    
    # Print the response
    print(f"Response: {response.text}")
    
    # Check if we have front matter
    content = response.text
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, content, re.DOTALL)
    if match:
        frontmatter_str, main_content = match.groups()
        frontmatter = yaml.safe_load(frontmatter_str)
        print("\nFront Matter:")
        print(json.dumps(frontmatter, indent=2, default=str))
        print("\nMarkdown Content:")
        print(main_content)
    else:
        print("\nNo frontmatter found in response")
        print(content)

