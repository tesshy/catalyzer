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
        """Convert URL content to markdown with front matter."""
        try:
            # Convert the URL to markdown
            result = self.markitdown.convert_url(url)

            # Extract title from the result or use URL as fallback
            title = result.title or url.split("/")[-1] or "Untitled"
            title = "Unko"
            # Create front matter with required fields
            front_matter = {
                "title": title,
                "author": "",
                "url": url,
                "tags": [],
                "locations": [url],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }

            # Format the front matter as YAML
            front_matter_yaml = yaml.safe_dump(front_matter, default_flow_style=False, allow_unicode=True)

            # Combine front matter and markdown content
            markdown_with_front_matter = f"---\n{front_matter_yaml}---\n\n{result.markdown}"

            return markdown_with_front_matter

        # Catch recursion failures that may occur anywhere in the routine
        except RecursionError as exc:        # pragma: no cover
            raise ValueError(
                f"Failed to generate markdown from URL '{url}': recursion depth exceeded"
            ) from exc
        # Normalise any other unexpected errors
        except Exception as exc:             # pragma: no cover
            raise ValueError(
                f"Failed to generate markdown from URL '{url}': {exc}"
            ) from exc


# グローバルインスタンス
_markdown_service = MarkdownService()


def get_markdown_service():
    """依存性注入用のファクトリ関数"""
    return _markdown_service