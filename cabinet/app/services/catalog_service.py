"""Catalog service for Catalyzer::Cabinet."""

import json
from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from pydantic import HttpUrl

from ..database import CabinetDB
from ..models import Catalog, CatalogCreate, CatalogUpdate
from ..tools.import_catalog import extract_frontmatter
from .vectorization_service import get_vectorization_service


class CatalogService:
    """Service for catalog operations."""

    def __init__(self, db: CabinetDB = Depends()):
        """Initialize the catalog service."""
        self.db = db
        self.vectorization_service = get_vectorization_service()

    def create_catalog(self, group_name: str, user_name: str, catalog: CatalogCreate) -> Catalog:
        """Create a new catalog entry."""
        catalog_dict = catalog.model_dump()
        
        # Ensure datetime objects are set
        now = datetime.now(timezone.utc)
        catalog_dict["created_at"] = catalog_dict.get("created_at") or now
        catalog_dict["updated_at"] = catalog_dict.get("updated_at") or now
        
        # Convert URLs to strings for database storage
        catalog_dict["url"] = str(catalog_dict["url"])
        catalog_dict["locations"] = [str(loc) for loc in catalog_dict["locations"]]
        
        # Generate vector from markdown content if not provided
        if not catalog_dict.get("vector") and catalog_dict.get("markdown"):
            vector = self.vectorization_service.vectorize_text(catalog_dict["markdown"])
            if vector:
                catalog_dict["vector"] = vector
        
        # Create the catalog entry
        result = self.db.create_catalog(group_name, user_name, catalog_dict)
        
        # Parse the properties field from JSON string if needed
        if "properties" in result and isinstance(result["properties"], str):
            result["properties"] = json.loads(result["properties"])
        
        # Convert back to the Catalog model
        return Catalog(**result)
    
    def create_catalog_from_markdown(self, group_name: str, user_name: str, markdown_content: str, filename: str = None) -> Catalog:
        """Create a new catalog entry from a markdown file content.
        
        Args:
            group_name: The group name
            user_name: The user name
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
            return self.create_catalog(group_name, user_name, catalog)
        except Exception as e:
            raise ValueError(f"Failed to create catalog from markdown: {str(e)}")

    def get_catalog(self, group_name: str, user_name: str, catalog_id: UUID) -> Optional[Catalog]:
        """Get a catalog entry by ID."""
        result = self.db.get_catalog_by_id(group_name, user_name, str(catalog_id))
        if not result:
            return None
            
        # Convert string URLs back to HttpUrl objects
        result["url"] = HttpUrl(result["url"])
        result["locations"] = [HttpUrl(loc) for loc in result["locations"]]
        
        # Parse the properties field from JSON string if needed
        if "properties" in result and isinstance(result["properties"], str):
            result["properties"] = json.loads(result["properties"])
        
        return Catalog(**result)

    def update_catalog(self, group_name: str, user_name: str, catalog_id: UUID, catalog_update: CatalogUpdate) -> Optional[Catalog]:
        """Update a catalog entry."""
        # First, check if the catalog exists
        existing = self.db.get_catalog_by_id(group_name, user_name, str(catalog_id))
        if not existing:
            return None
            
        # Update only the provided fields
        update_data = catalog_update.model_dump(exclude_unset=True)
        
        # Convert URLs to strings for database storage
        if "url" in update_data and update_data["url"]:
            update_data["url"] = str(update_data["url"])
        if "locations" in update_data and update_data["locations"]:
            update_data["locations"] = [str(loc) for loc in update_data["locations"]]
        
        # Re-generate vector if markdown content is updated
        if "markdown" in update_data and update_data["markdown"]:
            vector = self.vectorization_service.vectorize_text(update_data["markdown"])
            if vector:
                update_data["vector"] = vector
        
        # Update the catalog entry
        result = self.db.update_catalog(group_name, user_name, str(catalog_id), update_data)
        
        if result:
            # Convert string URLs back to HttpUrl objects
            result["url"] = HttpUrl(result["url"])
            result["locations"] = [HttpUrl(loc) for loc in result["locations"]]
            
            # Parse the properties field from JSON string if needed
            if "properties" in result and isinstance(result["properties"], str):
                result["properties"] = json.loads(result["properties"])
                
            return Catalog(**result)
        
        return None

    def delete_catalog(self, group_name: str, user_name: str, catalog_id: UUID) -> bool:
        """Delete a catalog entry."""
        return self.db.delete_catalog(group_name, user_name, str(catalog_id))

    def search_catalogs(self, group_name: str, user_name: str, tags: Optional[List[str]] = None, query: Optional[str] = None) -> List[Catalog]:
        """Search catalogs by tags and/or full-text search."""
        results = self.db.search_catalogs(group_name, user_name, tags, query)
        
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

    def vector_search_catalogs(self, group_name: str, user_name: str, query_text: str, limit: int = 10) -> List[Catalog]:
        """Search catalogs using vector similarity based on query text."""
        # Generate vector from query text
        query_vector = self.vectorization_service.vectorize_text(query_text)
        if not query_vector:
            # Fallback to regular text search if vectorization fails
            return self.search_catalogs(group_name, user_name, query=query_text)
        
        # Perform vector search
        results = self.db.vector_search_catalogs(group_name, user_name, query_vector, limit)
        
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