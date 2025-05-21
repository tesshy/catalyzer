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
    group_name: str = "default",
    user_name: str = "cabinet",
    db_path: str = DEFAULT_DB_PATH,
    db_file: str = DEFAULT_DB_FILE,
):
    """Get a DuckDB connection for the specified group."""
    # Check if MotherDuck token exists
    motherduck_token = os.environ.get("MOTHERDUCK_TOKEN")
    
    if motherduck_token:
        # Connect to MotherDuck
        conn = duckdb.connect(f"md:{group_name}")
        # Note: MotherDuck authentication is handled by the MOTHERDUCK_TOKEN environment variable
    else:
        # Fall back to local database
        # Create data directory if it doesn't exist
        os.makedirs(db_path, exist_ok=True)
        
        # Connect to the database
        db_file_path = os.path.join(db_path, db_file)
        conn = duckdb.connect(db_file_path)
    
    # Use the specified group (database) if not default
    if group_name != "default":
        conn.execute(f"CREATE SCHEMA IF NOT EXISTS \"{group_name}\"")
        conn.execute(f"SET search_path TO \"{group_name}\"")
    
    # Create the table if it doesn't exist
    create_table(conn, user_name)
    
    try:
        yield conn
    finally:
        conn.close()


def create_table(conn: duckdb.DuckDBPyConnection, table_name: str = "cabinet"):
    """Create the cabinet table if it doesn't exist."""
    conn.execute(f"""
    CREATE TABLE IF NOT EXISTS "{table_name}" (
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


def get_db():
    """Get a database connection for dependency injection."""
    # Always use in-memory database for testing, regardless of MotherDuck token availability
    conn = duckdb.connect(":memory:")  # Using in-memory database for testing
    create_table(conn, "cabinet")  # Create the table with correct schema
    yield conn
    conn.close()


class CabinetDB:
    """Cabinet database operations."""

    def __init__(self, conn: duckdb.DuckDBPyConnection = Depends(get_db), table_name: str = "cabinet"):
        """Initialize the CabinetDB with a connection."""
        self.conn = conn
        self.table_name = table_name

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
        
        query = f"INSERT INTO \"{self.table_name}\" ({columns}) VALUES ({placeholders}) RETURNING *"
        result = self.conn.execute(query, list(catalog_data.values())).fetchone()
        
        # Get the column names from the result
        columns = [col[0] for col in self.conn.description]
        return dict(zip(columns, result))

    def get_catalog_by_id(self, catalog_id: str) -> Optional[Dict[str, Any]]:
        """Get a catalog entry by ID."""
        result = self.conn.execute(
            f"SELECT * FROM \"{self.table_name}\" WHERE id = ?", [catalog_id]
        ).fetchone()
        
        if not result:
            return None
            
        columns = [col[0] for col in self.conn.description]
        return dict(zip(columns, result))

    def update_catalog(self, catalog_id: str, catalog_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a catalog entry."""
        # Update the updated_at timestamp
        catalog_data["updated_at"] = datetime.utcnow()
        
        # Build the SET clause
        set_clause = ", ".join([f"{key} = ?" for key in catalog_data.keys()])
        values = list(catalog_data.values())
        values.append(catalog_id)
        
        # Update the record
        query = f"UPDATE \"{self.table_name}\" SET {set_clause} WHERE id = ? RETURNING *"
        result = self.conn.execute(query, values).fetchone()
        
        if not result:
            return None
            
        columns = [col[0] for col in self.conn.description]
        return dict(zip(columns, result))

    def delete_catalog(self, catalog_id: str) -> bool:
        """Delete a catalog entry."""
        result = self.conn.execute(
            f"DELETE FROM \"{self.table_name}\" WHERE id = ? RETURNING id", [catalog_id]
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
            # Simple full-text search on title and markdown
            where_clauses.append("(title ILIKE ? OR markdown ILIKE ?)")
            params.extend([f"%{query}%", f"%{query}%"])
        
        # Construct the final query
        if where_clauses:
            where_clause = " AND ".join(where_clauses)
            sql_query = f"SELECT * FROM \"{self.table_name}\" WHERE {where_clause}"
        else:
            sql_query = f"SELECT * FROM \"{self.table_name}\""
        
        # Execute the query
        results = self.conn.execute(sql_query, params).fetchall()
        
        # Convert results to dictionaries
        columns = [col[0] for col in self.conn.description]
        return [dict(zip(columns, row)) for row in results]