"""Database operations for Catalyzer::Cabinet."""

import os
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

import duckdb
from fastapi import Depends


def get_db(org_name: str):
    """Get the connection string for a specific organization database."""
    # Check if MotherDuck token is available
    motherduck_token = os.environ.get("motherduck_token")
    if motherduck_token:
        print("Using MotherDuck for database storage.")
        conn = duckdb.connect("md:")
        conn.execute(f"CREATE DATABASE IF NOT EXISTS {org_name}")
        conn.execute(f"USE {org_name}")
    else:
        # Use local file-based storage per organization
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        os.makedirs(data_dir, exist_ok=True)
        conn = duckdb.connect(os.path.join(data_dir, f"{org_name}.duckdb"))

    # Set the connection to be persistent
    try:
        yield conn
    finally:
        conn.close()


def create_table(conn: duckdb.DuckDBPyConnection, group_name: str, user_name: str):
    """
    Create a table for a specific user in a specific group.
    
    Args:
        conn: DuckDB connection
        group_name: Name of the group (schema)
        user_name: Name of the user (table)
    """

    # Ensure schema (group) exists
    print(1)
    conn.execute(f"CREATE SCHEMA IF NOT EXISTS {group_name}")
    
    # Create table (user) in the schema if it doesn't exist
    conn.execute(f"""
    CREATE TABLE IF NOT EXISTS {group_name}.{user_name} (
        id UUID PRIMARY KEY,
        title VARCHAR,
        author VARCHAR,
        url VARCHAR,
        tags VARCHAR[],
        locations VARCHAR[],
        created_at TIMESTAMP,
        updated_at TIMESTAMP,
        markdown VARCHAR,
        properties JSON
    )
    """)


class CabinetDB:
    """Cabinet database operations."""

    def __init__(self, conn: duckdb.DuckDBPyConnection = Depends(get_db)):
        """Initialize the CabinetDB with a connection."""
        self.conn = conn

    def ensure_table_exists(self, group_name: str, user_name: str):
        """Ensure the group/user table exists."""
        create_table(self.conn, group_name, user_name)

    def create_catalog(self, group_name: str, user_name: str, catalog_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new catalog entry."""
        # Ensure the table exists
        self.ensure_table_exists(group_name, user_name)
        
        catalog_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        
        # Set created_at and updated_at if not provided
        catalog_data["id"] = catalog_id
        catalog_data["created_at"] = catalog_data.get("created_at", now)
        catalog_data["updated_at"] = catalog_data.get("updated_at", now)
        
        columns = ", ".join(catalog_data.keys())
        placeholders = ", ".join(["?" for _ in catalog_data.keys()])
        
        query = f"INSERT INTO {group_name}.{user_name} ({columns}) VALUES ({placeholders}) RETURNING *"
        print(query)
        result = self.conn.execute(query, list(catalog_data.values())).fetchone()
        
        # Get the column names from the result
        columns = [col[0] for col in self.conn.description]
        return dict(zip(columns, result))

    def get_catalog_by_id(self, group_name: str, user_name: str, catalog_id: str) -> Optional[Dict[str, Any]]:
        """Get a catalog entry by ID."""
        # Ensure the table exists
        self.ensure_table_exists(group_name, user_name)
        
        result = self.conn.execute(
            f"SELECT * FROM {group_name}.{user_name} WHERE id = ?", [catalog_id]
        ).fetchone()
        
        if not result:
            return None
            
        columns = [col[0] for col in self.conn.description]
        return dict(zip(columns, result))

    def update_catalog(self, group_name: str, user_name: str, catalog_id: str, catalog_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a catalog entry."""
        # Ensure the table exists
        self.ensure_table_exists(group_name, user_name)
        
        # Update the updated_at timestamp
        catalog_data["updated_at"] = datetime.now(timezone.utc)
        
        # Build the SET clause
        set_clause = ", ".join([f"{key} = ?" for key in catalog_data.keys()])
        values = list(catalog_data.values())
        values.append(catalog_id)
        
        # Update the record
        query = f"UPDATE {group_name}.{user_name} SET {set_clause} WHERE id = ? RETURNING *"
        result = self.conn.execute(query, values).fetchone()
        
        if not result:
            return None
            
        columns = [col[0] for col in self.conn.description]
        return dict(zip(columns, result))

    def delete_catalog(self, group_name: str, user_name: str, catalog_id: str) -> bool:
        """Delete a catalog entry."""
        # Ensure the table exists
        self.ensure_table_exists(group_name, user_name)
        
        result = self.conn.execute(
            f"DELETE FROM {group_name}.{user_name} WHERE id = ? RETURNING id", [catalog_id]
        ).fetchone()
        
        return bool(result)

    def search_catalogs(self, group_name: str, user_name: str, tags: Optional[List[str]] = None, query: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search catalogs by tags and/or full-text search."""
        # Ensure the table exists
        self.ensure_table_exists(group_name, user_name)
        
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
            # Simple full-text search on title and markdown content
            where_clauses.append("(title ILIKE ? OR markdown ILIKE ?)")
            params.extend([f"%{query}%", f"%{query}%"])
        
        # Construct the final query
        if where_clauses:
            where_clause = " AND ".join(where_clauses)
            sql_query = f"SELECT * FROM {group_name}.{user_name} WHERE {where_clause}"
        else:
            sql_query = f"SELECT * FROM {group_name}.{user_name}"
        
        # Execute the query
        results = self.conn.execute(sql_query, params).fetchall()
        
        # Convert results to dictionaries
        columns = [col[0] for col in self.conn.description]
        return [dict(zip(columns, row)) for row in results]