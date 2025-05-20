#!/usr/bin/env python3

import io
from fastapi import FastAPI, File, UploadFile, Depends
from fastapi.testclient import TestClient

app = FastAPI()

@app.post("/test")
async def test_endpoint(file: UploadFile = File(...)):
    """Test endpoint for debugging file uploads."""
    content = await file.read()
    content_str = content.decode("utf-8")
    print(f"File content: {content_str}")
    return {"filename": file.filename, "content_length": len(content_str)}

# Create a test client
client = TestClient(app)

# Test the endpoint with a file upload
def test_file_upload():
    # Create a test file
    markdown_content = """---
title: Test Markdown
author: test@example.com
url: https://example.com/test
tags:
  - test
  - markdown
locations:
  - https://example.com/test-data
---
# Test Markdown

This is a test markdown file.
"""
    file = io.BytesIO(markdown_content.encode("utf-8"))
    
    # Upload the file
    response = client.post(
        "/test",
        files={"file": ("test.md", file, "text/markdown")}
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.json()}")

if __name__ == "__main__":
    test_file_upload()