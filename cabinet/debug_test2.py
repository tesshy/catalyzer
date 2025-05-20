#!/usr/bin/env python3

import yaml
import re
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.testclient import TestClient

app = FastAPI()

@app.post("/test")
async def test_endpoint(request: Request):
    """Test endpoint for debugging."""
    content_type = request.headers.get("content-type")
    print(f"Content-Type: {content_type}")
    
    if content_type == "text/markdown":
        content = await request.body()
        try:
            content_str = content.decode("utf-8")
            print(f"Content received: {content_str}")
            return {"message": "Success", "content_type": content_type}
        except Exception as e:
            print(f"Error processing request: {e}")
            return {"message": f"Error: {str(e)}"}
    else:
        return {"message": "Wrong content type"}

# Create a test client
client = TestClient(app)

# Test the endpoint
def test_direct_markdown():
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

    # Send request with text/markdown content type
    response = client.post(
        "/test",
        content=markdown_content.encode("utf-8"),
        headers={"Content-Type": "text/markdown"}
    )
    
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.json()}")

if __name__ == "__main__":
    test_direct_markdown()