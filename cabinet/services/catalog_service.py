"""Catalog service for Catalyzer::Cabinet."""

import json
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from pydantic import HttpUrl

from ..database import CabinetDB
from ..models import Catalog, CatalogCreate, CatalogUpdate
from ..tools.import_catalog import extract_frontmatter


class CatalogService:
    """Service for catalog operations."""

    def __init__(self, db: CabinetDB = Depends()):
        """Initialize the catalog service."""
        self.db = db

    def create_catalog(self, catalog: CatalogCreate, group_name: str = "default", user_name: str = "cabinet") -> Catalog:
        """Create a new catalog entry."""
        catalog_dict = catalog.dict()
        
        # Ensure datetime objects are set
        now = datetime.utcnow()
        catalog_dict["created_at"] = catalog_dict.get("created_at") or now
        catalog_dict["updated_at"] = catalog_dict.get("updated_at") or now
        
        # Convert URLs to strings for database storage
        catalog_dict["url"] = str(catalog_dict["url"])
        catalog_dict["locations"] = [str(loc) for loc in catalog_dict["locations"]]
        
        # Set group and table name in the db
        self.db.conn.execute(f"CREATE SCHEMA IF NOT EXISTS {group_name}")
        self.db.conn.execute(f"SET search_path TO {group_name}")
        self.db.table_name = user_name
        
        # Create the table if it doesn't exist with the user_name
        create_table(self.db.conn, user_name)
        
        # Create the catalog entry
        result = self.db.create_catalog(catalog_dict)
        
        # Parse the properties field from JSON string if needed
        if "properties" in result and isinstance(result["properties"], str):
            result["properties"] = json.loads(result["properties"])
        
        # Convert back to the Catalog model
        return Catalog(**result)
    
    def create_catalog_from_markdown(self, markdown_content: str, filename: str = None) -> Catalog:
        """Create a new catalog entry from a markdown file content.
        
        Args:
            markdown_content: The content of the markdown file
            filename: Optional filename to use as a fallback for missing title
            
        Returns:
            The created catalog
        """
        try:
            # Extract frontmatter and content
            frontmatter, content = extract_frontmatter(markdown_content)
            
            # Prepare catalog data with proper types
            catalog_data = {
                "title": frontmatter.get("title", filename or "Untitled"),
                "author": frontmatter.get("author", ""),
                "url": HttpUrl(frontmatter.get("url", "https://example.com/")),
                "tags": frontmatter.get("tags", []),
                "locations": [HttpUrl(loc) for loc in frontmatter.get("locations", [])],
                "markdown": content,
                "properties": frontmatter,
            }
            
            # Add optional timestamp fields if present
            if "created_at" in frontmatter:
                catalog_data["created_at"] = frontmatter["created_at"]
            if "updated_at" in frontmatter:
                catalog_data["updated_at"] = frontmatter["updated_at"]
            
            # Create catalog
            catalog = CatalogCreate(**catalog_data)
            return self.create_catalog(catalog)
        except Exception as e:
            raise ValueError(f"Failed to create catalog from markdown: {str(e)}")

    def get_catalog(self, catalog_id: UUID, group_name: str = "default", user_name: str = "cabinet") -> Optional[Catalog]:
        """Get a catalog entry by ID."""
        # Set group and table name in the db
        self.db.conn.execute(f"CREATE SCHEMA IF NOT EXISTS {group_name}")
        self.db.conn.execute(f"SET search_path TO {group_name}")
        self.db.table_name = user_name
        
        result = self.db.get_catalog_by_id(str(catalog_id))
        if not result:
            return None
            
        # Convert string URLs back to HttpUrl objects
        result["url"] = HttpUrl(result["url"])
        result["locations"] = [HttpUrl(loc) for loc in result["locations"]]
        
        # Parse the properties field from JSON string if needed
        if "properties" in result and isinstance(result["properties"], str):
            result["properties"] = json.loads(result["properties"])
        
        return Catalog(**result)

    def update_catalog(self, catalog_id: UUID, catalog_update: CatalogUpdate, group_name: str = "default", user_name: str = "cabinet") -> Optional[Catalog]:
        """Update a catalog entry."""
        # Set group and table name in the db
        self.db.conn.execute(f"CREATE SCHEMA IF NOT EXISTS {group_name}")
        self.db.conn.execute(f"SET search_path TO {group_name}")
        self.db.table_name = user_name
        
        # First, check if the catalog exists
        existing = self.db.get_catalog_by_id(str(catalog_id))
        if not existing:
            return None
            
        # Update only the provided fields
        update_data = catalog_update.dict(exclude_unset=True)
        
        # Convert URLs to strings for database storage
        if "url" in update_data and update_data["url"]:
            update_data["url"] = str(update_data["url"])
        if "locations" in update_data and update_data["locations"]:
            update_data["locations"] = [str(loc) for loc in update_data["locations"]]
        
        # Update the catalog entry
        result = self.db.update_catalog(str(catalog_id), update_data)
        
        if result:
            # Convert string URLs back to HttpUrl objects
            result["url"] = HttpUrl(result["url"])
            result["locations"] = [HttpUrl(loc) for loc in result["locations"]]
            
            # Parse the properties field from JSON string if needed
            if "properties" in result and isinstance(result["properties"], str):
                result["properties"] = json.loads(result["properties"])
                
            return Catalog(**result)
        
        return None

    def delete_catalog(self, catalog_id: UUID, group_name: str = "default", user_name: str = "cabinet") -> bool:
        """Delete a catalog entry."""
        # Set group and table name in the db
        self.db.conn.execute(f"CREATE SCHEMA IF NOT EXISTS {group_name}")
        self.db.conn.execute(f"SET search_path TO {group_name}")
        self.db.table_name = user_name
        
        return self.db.delete_catalog(str(catalog_id))

    def search_catalogs(self, tags: Optional[List[str]] = None, query: Optional[str] = None, group_name: str = "default", user_name: str = "cabinet") -> List[Catalog]:
        """Search catalogs by tags and/or full-text search."""
        # Set group and table name in the db
        self.db.conn.execute(f"CREATE SCHEMA IF NOT EXISTS {group_name}")
        self.db.conn.execute(f"SET search_path TO {group_name}")
        self.db.table_name = user_name
        
        results = self.db.search_catalogs(tags, query)
        
        # Convert to Catalog models
        catalogs = []
        for result in results:
            # Convert string URLs to HttpUrl objects
            result["url"] = HttpUrl(result["url"])
            result["locations"] = [HttpUrl(loc) for loc in result["locations"]]
            
            # Parse the properties field from JSON string if needed
            if "properties" in result and isinstance(result["properties"], str):
                result["properties"] = json.loads(result["properties"])
                
            catalogs.append(Catalog(**result))
        
        return catalogs