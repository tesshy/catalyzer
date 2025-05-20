#!/usr/bin/env python3

import yaml
import re
from pydantic import HttpUrl

def extract_frontmatter(content):
    """Extract YAML frontmatter from markdown content."""
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, content, re.DOTALL)
    
    if not match:
        raise ValueError("Invalid markdown format: Missing frontmatter")
    
    frontmatter_str, main_content = match.groups()
    print(f"FRONTMATTER STR:\n{frontmatter_str}")
    frontmatter = yaml.safe_load(frontmatter_str)
    print(f"PARSED FRONTMATTER: {frontmatter}")
    
    return frontmatter, main_content

def create_catalog_from_markdown(markdown_content, filename=None):
    """Mock of catalog creation from markdown."""
    try:
        # Extract frontmatter and content
        frontmatter, content = extract_frontmatter(markdown_content)
        
        # Prepare catalog data with proper types
        catalog_data = {
            "title": frontmatter.get("title", filename or "Untitled"),
            "author": frontmatter.get("author", ""),
            "url": HttpUrl(frontmatter.get("url", "https://example.com/")),
            "tags": frontmatter.get("tags", []),
            "locations": [HttpUrl(loc) for loc in frontmatter.get("locations", [])],
            "content": content,
        }
        
        # Add optional timestamp fields if present
        if "created_at" in frontmatter:
            catalog_data["created_at"] = frontmatter["created_at"]
        if "updated_at" in frontmatter:
            catalog_data["updated_at"] = frontmatter["updated_at"]
            
        print("Catalog data prepared successfully!")
        print(f"Title: {catalog_data['title']}")
        print(f"Author: {catalog_data['author']}")
        print(f"URL: {catalog_data['url']}")
        print(f"Tags: {catalog_data['tags']}")
        print(f"Locations: {catalog_data['locations']}")
        print(f"Content: {catalog_data['content'][:30]}...")
        
        return catalog_data
        
    except Exception as e:
        print(f"Error: {e}")
        raise

# Test with the sample markdown from our test
markdown_content = """---
title: Direct Markdown
author: direct@example.com
url: https://example.com/direct
tags:
  - direct
  - markdown
locations:
  - https://example.com/direct-data
---
# Direct Markdown

This is markdown content sent directly with content-type text/markdown.
"""

try:
    result = create_catalog_from_markdown(markdown_content, "test.md")
    print("Success!")
except Exception as e:
    print(f"Error: {e}")