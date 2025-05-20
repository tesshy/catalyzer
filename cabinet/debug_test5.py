#!/usr/bin/env python3

import duckdb
import pytest
import os

from cabinet.services.catalog_service import CatalogService
from cabinet.database import CabinetDB

# Create a test database
def get_test_db():
    """Create a temporary test database."""
    # Use an in-memory database for testing
    conn = duckdb.connect(":memory:")
    
    # Create the test table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS cabinet (
        id UUID PRIMARY KEY,
        title VARCHAR,
        author VARCHAR,
        url VARCHAR,
        tags VARCHAR[],
        locations VARCHAR[],
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        content VARCHAR
    )
    """)
    
    return conn

# Create a test markdown document
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

# Test create_catalog_from_markdown
def test_create_from_markdown():
    db_conn = get_test_db()
    db = CabinetDB(db_conn)
    service = CatalogService(db)
    
    try:
        # Create a catalog from markdown
        print("Creating catalog from markdown...")
        catalog = service.create_catalog_from_markdown(markdown_content, "test.md")
        
        print("Catalog created successfully!")
        print(f"Title: {catalog.title}")
        print(f"Author: {catalog.author}")
        print(f"URL: {catalog.url}")
        print(f"Tags: {catalog.tags}")
        print(f"Locations: {catalog.locations}")
        print(f"Content: {catalog.content[:30]}...")
        
        # Verify the catalog was created correctly
        print("\nVerifying catalog attributes...")
        assert catalog.title == "Direct Markdown"
        assert catalog.author == "direct@example.com"
        assert str(catalog.url) == "https://example.com/direct"
        assert catalog.tags == ["direct", "markdown"]
        assert str(catalog.locations[0]) == "https://example.com/direct-data"
        assert catalog.content.startswith("# Direct Markdown")
        print("All attributes verified correctly!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        db_conn.close()

if __name__ == "__main__":
    test_create_from_markdown()