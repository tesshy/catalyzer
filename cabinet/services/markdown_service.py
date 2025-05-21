"""Service for markdown conversion operations."""

from datetime import datetime
from typing import Optional
import yaml
from fastapi import Depends
from markitdown import MarkItDown
from markitdown._base_converter import DocumentConverterResult


class MarkdownService:
    """Service for markdown conversion operations."""

    def __init__(self, markitdown_client=None):
        """Initialize the service."""
        self.markitdown = markitdown_client or MarkItDown()

    def convert_url_to_markdown(self, url: str) -> str:
        """Convert URL content to markdown with front matter.
        
        Args:
            url: The URL to fetch and convert
            
        Returns:
            Markdown content with front matter
            
        Raises:
            ValueError: If the URL is invalid or content cannot be converted
        """
        # Convert the URL to markdown
        result = self.markitdown.convert_url(url)
        
        # Extract title from the result or use URL as fallback
        title = result.title or url.split("/")[-1] or "Untitled"
        
        # Create front matter with required fields
        front_matter = {
            "title": title,
            "author": "",
            "url": url,
            "tags": [],
            "locations": [url],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        # Format the front matter as YAML
        front_matter_yaml = yaml.dump(front_matter, default_flow_style=False)
        
        # Combine front matter and markdown content
        markdown_with_front_matter = f"---\n{front_matter_yaml}---\n\n{result.markdown}"
        
        return markdown_with_front_matter


# グローバルインスタンス
_markdown_service = MarkdownService()


def get_markdown_service():
    """依存性注入用のファクトリ関数"""
    return _markdown_service