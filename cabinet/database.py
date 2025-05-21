"""Database operations for Catalyzer::Cabinet."""

import os
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

import duckdb
from fastapi import Depends


# Use a single in-memory database connection
DB_CONNECTION = duckdb.connect(":memory:")

def create_table(conn: duckdb.DuckDBPyConnection):
    """Create the cabinet table if it doesn't exist."""
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
        content VARCHAR,
        properties JSON
    )
    """)


# Initialize the table
create_table(DB_CONNECTION)


def get_db():
    """Get a database connection for dependency injection."""
    yield DB_CONNECTION


class CabinetDB:
    """Cabinet database operations."""

    def __init__(self, conn: duckdb.DuckDBPyConnection = Depends(get_db)):
        """Initialize the CabinetDB with a connection."""
        self.conn = conn

    def create_catalog(self, catalog_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new catalog entry."""
        catalog_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        
        # Set created_at and updated_at if not provided
        catalog_data["id"] = catalog_id
        catalog_data["created_at"] = catalog_data.get("created_at", now)
        catalog_data["updated_at"] = catalog_data.get("updated_at", now)
        
        columns = ", ".join(catalog_data.keys())
        placeholders = ", ".join(["?" for _ in catalog_data.keys()])
        
        query = f"INSERT INTO cabinet ({columns}) VALUES ({placeholders}) RETURNING *"
        result = self.conn.execute(query, list(catalog_data.values())).fetchone()
        
        # Get the column names from the result
        columns = [col[0] for col in self.conn.description]
        return dict(zip(columns, result))

    def get_catalog_by_id(self, catalog_id: str) -> Optional[Dict[str, Any]]:
        """Get a catalog entry by ID."""
        result = self.conn.execute(
            "SELECT * FROM cabinet WHERE id = ?", [catalog_id]
        ).fetchone()
        
        if not result:
            return None
            
        columns = [col[0] for col in self.conn.description]
        return dict(zip(columns, result))

    def update_catalog(self, catalog_id: str, catalog_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a catalog entry."""
        # Update the updated_at timestamp
        catalog_data["updated_at"] = datetime.now(timezone.utc)
        
        # Build the SET clause
        set_clause = ", ".join([f"{key} = ?" for key in catalog_data.keys()])
        values = list(catalog_data.values())
        values.append(catalog_id)
        
        # Update the record
        query = f"UPDATE cabinet SET {set_clause} WHERE id = ? RETURNING *"
        result = self.conn.execute(query, values).fetchone()
        
        if not result:
            return None
            
        columns = [col[0] for col in self.conn.description]
        return dict(zip(columns, result))

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
        
        # Construct the final query
        if where_clauses:
            where_clause = " AND ".join(where_clauses)
            sql_query = f"SELECT * FROM cabinet WHERE {where_clause}"
        else:
            sql_query = "SELECT * FROM cabinet"
        
        # Execute the query
        results = self.conn.execute(sql_query, params).fetchall()
        
        # Convert results to dictionaries
        columns = [col[0] for col in self.conn.description]
        return [dict(zip(columns, row)) for row in results]