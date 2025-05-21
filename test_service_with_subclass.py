#!/usr/bin/env python3

from cabinet.services.markdown_service import MarkdownService
from markitdown._base_converter import DocumentConverterResult
from unittest.mock import Mock
import yaml
import re

class MockMarkItDown:
    """Mock class for MarkItDown."""
    
    def convert_url(self, url):
        """Mock implementation of convert_url."""
        print(f"Mock called with URL: {url}")
        return DocumentConverterResult(
            markdown="# Mocked Title\n\nThis is mocked content.",
            title="Mocked Title"
        )

# Create a modified version of the MarkdownService
class TestMarkdownService(MarkdownService):
    """Test version of MarkdownService with mock."""
    
    def __init__(self):
        """Override initialization."""
        # Don't call super().__init__()
        self.markitdown = MockMarkItDown()

# Test the service
service = TestMarkdownService()
result = service.convert_url_to_markdown("https://example.com")

# Validate the result
pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
match = re.match(pattern, result, re.DOTALL)
assert match is not None, "Result should contain frontmatter"

frontmatter_str, main_content = match.groups()
frontmatter = yaml.safe_load(frontmatter_str)

print("Frontmatter:")
for key, value in frontmatter.items():
    print(f"  {key}: {value}")

print("\nContent:")
print(main_content)

print("\nTest passed!")