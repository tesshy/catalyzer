#!/usr/bin/env python3

import io
import re
import yaml
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, status, UploadFile, File
from fastapi.testclient import TestClient
from typing import List, Optional
from pydantic import BaseModel, HttpUrl

# Define models
class CatalogBase(BaseModel):
    title: str
    author: str
    url: HttpUrl
    tags: List[str] = []
    locations: List[HttpUrl] = []
    content: str

class CatalogCreate(CatalogBase):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class Catalog(CatalogBase):
    id: str
    created_at: datetime
    updated_at: datetime

# Create a simple app
app = FastAPI()

@app.post("/catalogs/new", response_model=Catalog, status_code=status.HTTP_201_CREATED)
async def upload_markdown(
    request: Request,
    file: UploadFile = File(None)
):
    """Create a new catalog entry from a Markdown file upload or direct text/markdown content."""
    markdown_content = None
    filename = "document.md"
    
    # Handle file upload
    if file:
        filename = file.filename
        content = await file.read()
        markdown_content = content.decode("utf-8")
    
    # Handle direct text/markdown content
    elif request.headers.get("content-type") == "text/markdown":
        content = await request.body()
        markdown_content = content.decode("utf-8")
    
    # Neither file nor text/markdown content provided
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content-Type must be text/markdown when not using multipart/form-data",
        )
    
    # Process the markdown content
    try:
        # Extract YAML frontmatter using regex
        pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
        match = re.match(pattern, markdown_content, re.DOTALL)
        
        if not match:
            raise ValueError("Invalid markdown format: Missing frontmatter")
        
        frontmatter_str, main_content = match.groups()
        
        # Parse YAML frontmatter
        frontmatter = yaml.safe_load(frontmatter_str)
        if not isinstance(frontmatter, dict):
            raise ValueError("Frontmatter is not a dictionary")
            
        # Create catalog data
        now = datetime.now()
        
        # Create catalog (simplified for test)
        catalog = {
            "id": "test-id-123",
            "title": frontmatter.get("title", filename),
            "author": frontmatter.get("author", ""),
            "url": HttpUrl(frontmatter.get("url", "https://example.com/")),
            "tags": frontmatter.get("tags", []),
            "locations": [HttpUrl(loc) for loc in frontmatter.get("locations", [])],
            "content": main_content,
            "created_at": frontmatter.get("created_at", now),
            "updated_at": frontmatter.get("updated_at", now),
        }
        
        return catalog
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse markdown: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create catalog: {str(e)}",
        )

# Create a test client
client = TestClient(app)

def test_direct_upload():
    """Test direct markdown upload."""
    # Create a test markdown content
    markdown_content = """---
title: Test Direct Upload
author: direct@example.com
url: https://example.com/direct
---
# Test Direct Upload

This is direct markdown content.
"""
    
    # Upload directly
    print("\nTesting direct markdown upload...")
    response = client.post(
        "/catalogs/new",
        content=markdown_content.encode("utf-8"),
        headers={"Content-Type": "text/markdown"}
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.json()}")

def test_file_upload():
    """Test file upload."""
    # Create a test markdown content
    markdown_content = """---
title: Test File Upload
author: file@example.com
url: https://example.com/file
---
# Test File Upload

This is a file upload test.
"""

    file = io.BytesIO(markdown_content.encode("utf-8"))
    
    # Upload file
    print("\nTesting file upload...")
    response = client.post(
        "/catalogs/new",
        files={"file": ("test.md", file, "text/markdown")}
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.json()}")

if __name__ == "__main__":
    test_direct_upload()
    test_file_upload()