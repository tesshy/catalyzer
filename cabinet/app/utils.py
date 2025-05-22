"""Utility functions for Catalyzer::Cabinet."""

from typing import Dict, Any, Tuple, List
import re
import yaml


def parse_markdown_with_metadata(content: str) -> Tuple[Dict[str, Any], str]:
    """Parse markdown content with metadata using YAML frontmatter.
    
    Args:
        content: Markdown content with YAML frontmatter
        
    Returns:
        Tuple of (metadata_dict, content_str)
    """
    # Extract YAML frontmatter using regex
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, content, re.DOTALL)
    
    if not match:
        raise ValueError("No metadata found in markdown file")
    
    frontmatter_str, main_content = match.groups()
    
    try:
        # Parse the YAML frontmatter
        metadata = yaml.safe_load(frontmatter_str)
        if not isinstance(metadata, dict):
            raise ValueError("Invalid frontmatter: not a dictionary")
    except Exception as e:
        raise ValueError(f"Failed to parse frontmatter: {str(e)}")
    
    return metadata, main_content