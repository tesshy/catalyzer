"""Utility functions for Catalyzer::Cabinet."""

from typing import Dict, Any, Tuple
import markdown
from markdown.extensions.meta import MetaExtension


def parse_markdown_with_metadata(content: str) -> Tuple[Dict[str, Any], str]:
    """Parse markdown content with metadata using python-markdown's meta-data extension.
    
    Args:
        content: Markdown content with YAML frontmatter
        
    Returns:
        Tuple of (metadata_dict, html_content)
    """
    md = markdown.Markdown(extensions=[MetaExtension()])
    html_content = md.convert(content)
    
    # Convert metadata to appropriate types
    metadata = {}
    
    for key, values in md.Meta.items():
        # The meta extension returns all values as lists of strings
        if len(values) == 1:
            # Single values are returned as the first item
            value = values[0]
            
            # Handle special cases for known types
            if key == "tags" and value.startswith("[") and value.endswith("]"):
                # Convert string representation of list to actual list
                # Format: [tag1, tag2, tag3]
                tags_str = value.strip("[]")
                metadata[key] = [tag.strip() for tag in tags_str.split(",")] if tags_str else []
            elif key == "locations" and value.startswith("[") and value.endswith("]"):
                # Convert string representation of list to actual list
                locations_str = value.strip("[]")
                metadata[key] = [loc.strip() for loc in locations_str.split(",")] if locations_str else []
            else:
                metadata[key] = value
        else:
            # Multiple values are kept as a list
            metadata[key] = values
    
    return metadata, html_content