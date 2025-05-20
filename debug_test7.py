#!/usr/bin/env python3

import io
import yaml
import re
from fastapi import FastAPI, File, UploadFile, Depends, Request
from fastapi.testclient import TestClient
from pydantic import HttpUrl, BaseModel
from typing import List, Optional

# Create a simple model for testing
class TestCatalog(BaseModel):
    title: str
    author: str
    url: HttpUrl
    tags: List[str]
    locations: List[HttpUrl]
    content: str

app = FastAPI()

@app.post("/test-file")
async def test_file_endpoint(file: UploadFile = File(...)):
    """Test endpoint for debugging file uploads."""
    content = await file.read()
    content_str = content.decode("utf-8")
    
    # Extract YAML frontmatter
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, content_str, re.DOTALL)
    
    if not match:
        return {"error": "Invalid markdown format"}
    
    frontmatter_str, main_content = match.groups()
    frontmatter = yaml.safe_load(frontmatter_str)
    
    # Create catalog data
    catalog = TestCatalog(
        title=frontmatter.get("title", file.filename),
        author=frontmatter.get("author", ""),
        url=HttpUrl(frontmatter.get("url", "https://example.com/")),
        tags=frontmatter.get("tags", []),
        locations=[HttpUrl(loc) for loc in frontmatter.get("locations", [])],
        content=main_content
    )
    
    return {"success": True, "catalog": catalog.dict()}

@app.post("/test-direct")
async def test_direct_endpoint(request: Request):
    """Test endpoint for debugging direct text/markdown uploads."""
    if request.headers.get("content-type") != "text/markdown":
        return {"error": "Content-Type must be text/markdown"}
    
    content = await request.body()
    content_str = content.decode("utf-8")
    
    # Extract YAML frontmatter
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, content_str, re.DOTALL)
    
    if not match:
        return {"error": "Invalid markdown format"}
    
    frontmatter_str, main_content = match.groups()
    frontmatter = yaml.safe_load(frontmatter_str)
    
    # Create catalog data
    catalog = TestCatalog(
        title=frontmatter.get("title", "document.md"),
        author=frontmatter.get("author", ""),
        url=HttpUrl(frontmatter.get("url", "https://example.com/")),
        tags=frontmatter.get("tags", []),
        locations=[HttpUrl(loc) for loc in frontmatter.get("locations", [])],
        content=main_content
    )
    
    return {"success": True, "catalog": catalog.dict()}

# Create a test client
client = TestClient(app)

def test_file_upload():
    """Test uploading a file."""
    # Create a test file
    markdown_content = """---
title: Test File Upload
author: test@example.com
url: https://example.com/test
tags:
  - test
  - file
locations:
  - https://example.com/test-data
---
# Test File Upload

This is a test markdown file.
"""
    file = io.BytesIO(markdown_content.encode("utf-8"))
    
    # Upload the file
    response = client.post(
        "/test-file",
        files={"file": ("test.md", file, "text/markdown")}
    )
    
    print(f"File upload response status: {response.status_code}")
    print(f"File upload response: {response.json()}")

def test_direct_upload():
    """Test direct markdown upload."""
    # Create a test markdown content
    markdown_content = """---
title: Test Direct Upload
author: direct@example.com
url: https://example.com/direct
tags:
  - test
  - direct
locations:
  - https://example.com/direct-data
---
# Test Direct Upload

This is direct markdown content.
"""
    
    # Upload directly
    response = client.post(
        "/test-direct",
        content=markdown_content.encode("utf-8"),
        headers={"Content-Type": "text/markdown"}
    )
    
    print(f"Direct upload response status: {response.status_code}")
    print(f"Direct upload response: {response.json()}")

if __name__ == "__main__":
    print("\n--- Testing file upload ---")
    test_file_upload()
    
    print("\n--- Testing direct upload ---")
    test_direct_upload()