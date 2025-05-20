"""Database operations for Catalyzer::Cabinet."""

import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

import duckdb
from fastapi import Depends

# Default database path if not specified
DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "data")
DEFAULT_DB_FILE = "cabinet.duckdb"


def get_db_connection(
    group: str = "default",
    db_path: str = DEFAULT_DB_PATH,
    db_file: str = DEFAULT_DB_FILE,
):
    """Get a DuckDB connection for the specified group."""
    # Create data directory if it doesn't exist
    os.makedirs(db_path, exist_ok=True)
    
    # Connect to the database
    db_file_path = os.path.join(db_path, db_file)
    conn = duckdb.connect(db_file_path)
    
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
    
    try:
        yield conn
    finally:
        conn.close()


def get_db():
    """Get a database connection for dependency injection."""
    for conn in get_db_connection():
        yield conn


class CabinetDB:
    """Cabinet database operations."""

    def __init__(self, conn: duckdb.DuckDBPyConnection = Depends(get_db)):
        """Initialize the CabinetDB with a connection."""
        self.conn = conn

    def create_catalog(self, catalog_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new catalog entry."""
        catalog_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Set created_at and updated_at if not provided
        catalog_data["id"] = catalog_id
        catalog_data["created_at"] = catalog_data.get("created_at", now)
        catalog_data["updated_at"] = catalog_data.get("updated_at", now)
        
        columns = ", ".join(catalog_data.keys())
        placeholders = ", ".join(["?" for _ in catalog_data.keys()])
        
        query = f"INSERT INTO cabinet ({columns}) VALUES ({placeholders})"
        self.conn.execute(query, list(catalog_data.values()))
        
        # Fetch the inserted record using get_catalog_by_id
        return self.get_catalog_by_id(catalog_id)

    def get_catalog_by_id(self, catalog_id: str) -> Optional[Dict[str, Any]]:
        """Get a catalog entry by ID."""
        # Explicitly list all columns to ensure correct order
        query = """
        SELECT id, title, author, url, tags, locations, created_at, updated_at, content 
        FROM cabinet WHERE id = ?
        """
        result = self.conn.execute(query, [catalog_id]).fetchone()
        
        if not result:
            return None
            
        # Create a dictionary with explicit field names instead of relying on description
        return {
            "id": result[0],
            "title": result[1],
            "author": result[2],
            "url": result[3],
            "tags": result[4],
            "locations": result[5],
            "created_at": result[6],
            "updated_at": result[7],
            "content": result[8]
        }

    def update_catalog(self, catalog_id: str, catalog_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a catalog entry."""
        # Update the updated_at timestamp
        catalog_data["updated_at"] = datetime.utcnow()
        
        # Build the SET clause
        set_clause = ", ".join([f"{key} = ?" for key in catalog_data.keys()])
        values = list(catalog_data.values())
        values.append(catalog_id)
        
        # Update the record using an explicit SELECT statement afterward to ensure we get all fields in the correct order
        self.conn.execute(f"UPDATE cabinet SET {set_clause} WHERE id = ?", values)
        
        # Get the updated record with fields in a specific order
        return self.get_catalog_by_id(catalog_id)

    def delete_catalog(self, catalog_id: str) -> bool:
        """Delete a catalog entry."""
        result = self.conn.execute(
            "DELETE FROM cabinet WHERE id = ? RETURNING id", [catalog_id]
        ).fetchone()
        
        return bool(result)

    def search_catalogs(self, tags: Optional[List[str]] = None, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search catalogs by tags and/or full-text search."""
        where_clauses = []
        params = []
        
        if tags:
            # Search for catalogs that have ANY of the specified tags
            tag_conditions = []
            for tag in tags:
                tag_conditions.append("? = ANY(tags)")
                params.append(tag)
            where_clauses.append(f"({' OR '.join(tag_conditions)})")
        
        if query:
            # Simple full-text search on title and content
            where_clauses.append("(title ILIKE ? OR content ILIKE ?)")
            params.extend([f"%{query}%", f"%{query}%"])
        
        # Construct the final query with explicit column selection
        select_clause = "SELECT id, title, author, url, tags, locations, created_at, updated_at, content"
        from_clause = "FROM cabinet"
        
        if where_clauses:
            where_clause = " AND ".join(where_clauses)
            sql_query = f"{select_clause} {from_clause} WHERE {where_clause}"
        else:
            sql_query = f"{select_clause} {from_clause}"
        
        # Execute the query
        results = self.conn.execute(sql_query, params).fetchall()
        
        # Convert results to dictionaries with explicit field mapping
        return [
            {
                "id": row[0],
                "title": row[1],
                "author": row[2],
                "url": row[3],
                "tags": row[4],
                "locations": row[5],
                "created_at": row[6],
                "updated_at": row[7],
                "content": row[8]
            }
            for row in results
        ]
        
    def clear_all_catalogs(self) -> None:
        """Clear all catalog entries (for testing purposes only)."""
        self.conn.execute("DELETE FROM cabinet")