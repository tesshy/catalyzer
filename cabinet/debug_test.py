#!/usr/bin/env python3

import yaml
import re

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
    frontmatter, content = extract_frontmatter(markdown_content)
    print("Frontmatter extraction successful!")
    print(f"URL type: {type(frontmatter.get('url'))}")
    print(f"Tags type: {type(frontmatter.get('tags'))}")
    print(f"Locations type: {type(frontmatter.get('locations'))}")
except Exception as e:
    print(f"Error: {e}")