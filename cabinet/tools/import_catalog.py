#!/usr/bin/env python3
"""Import catalog markdown files into the database."""

import argparse
import os
import re
import sys
import uuid
from datetime import datetime
from typing import Dict, List, Any, Tuple

import duckdb
import yaml


def extract_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """Extract YAML frontmatter from markdown content."""
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, content, re.DOTALL)
    
    if not match:
        raise ValueError("Invalid markdown format: Missing frontmatter")
    
    frontmatter_str, main_content = match.groups()
    frontmatter = yaml.safe_load(frontmatter_str)
    
    return frontmatter, main_content


def import_catalog(file_path: str, conn: duckdb.DuckDBPyConnection, group: str = "default") -> str:
    """Import a catalog markdown file into the database."""
    # Read the file
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract frontmatter and content
    frontmatter, main_content = extract_frontmatter(content)
    
    # Use the specified group (database) if not default
    if group != "default":
        conn.execute(f"CREATE SCHEMA IF NOT EXISTS {group}")
        conn.execute(f"SET search_path TO {group}")
    
    # Create the table if it doesn't exist
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
    
    # Prepare the data
    catalog_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    catalog_data = {
        "id": catalog_id,
        "title": frontmatter.get("title", ""),
        "author": frontmatter.get("author", ""),
        "url": frontmatter.get("url", ""),
        "tags": frontmatter.get("tags", []),
        "locations": frontmatter.get("locations", []),
        "created_at": frontmatter.get("created_at", now),
        "updated_at": frontmatter.get("updated_at", now),
        "content": main_content,
    }
    
    # Insert the data
    columns = ", ".join(catalog_data.keys())
    placeholders = ", ".join(["?" for _ in catalog_data.keys()])
    
    conn.execute(
        f"INSERT INTO cabinet ({columns}) VALUES ({placeholders})",
        list(catalog_data.values()),
    )
    
    return catalog_id


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Import catalog markdown files into the database")
    parser.add_argument("file", help="Path to the catalog markdown file or directory")
    parser.add_argument("--db", help="Path to the database file", default=":memory:")
    parser.add_argument("--group", help="Group (schema) to use", default="default")
    
    args = parser.parse_args()
    
    # Connect to the database
    conn = duckdb.connect(args.db)
    
    try:
        if os.path.isdir(args.file):
            # Import all markdown files in the directory
            for root, _, files in os.walk(args.file):
                for file in files:
                    if file.endswith(".md"):
                        file_path = os.path.join(root, file)
                        catalog_id = import_catalog(file_path, conn, args.group)
                        print(f"Imported {file_path} as {catalog_id}")
        else:
            # Import a single file
            catalog_id = import_catalog(args.file, conn, args.group)
            print(f"Imported {args.file} as {catalog_id}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()