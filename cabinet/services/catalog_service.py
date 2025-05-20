"""Catalog service for Catalyzer::Cabinet."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from pydantic import HttpUrl

from ..database import CabinetDB
from ..models import Catalog, CatalogCreate, CatalogUpdate


class CatalogService:
    """Service for catalog operations."""

    def __init__(self, db: CabinetDB = Depends()):
        """Initialize the catalog service."""
        self.db = db

    def create_catalog(self, catalog: CatalogCreate) -> Catalog:
        """Create a new catalog entry."""
        catalog_dict = catalog.dict()
        
        # Ensure datetime objects are set
        now = datetime.utcnow()
        catalog_dict["created_at"] = catalog_dict.get("created_at") or now
        catalog_dict["updated_at"] = catalog_dict.get("updated_at") or now
        
        # Convert URLs to strings for database storage
        catalog_dict["url"] = str(catalog_dict["url"])
        catalog_dict["locations"] = [str(loc) for loc in catalog_dict["locations"]]
        
        # Create the catalog entry
        result = self.db.create_catalog(catalog_dict)
        
        # Convert back to the Catalog model
        return Catalog(**result)

    def get_catalog(self, catalog_id: UUID) -> Optional[Catalog]:
        """Get a catalog entry by ID."""
        result = self.db.get_catalog_by_id(str(catalog_id))
        if not result:
            return None
            
        # Convert string URLs back to HttpUrl objects
        result["url"] = HttpUrl(result["url"])
        result["locations"] = [HttpUrl(loc) for loc in result["locations"]]
        
        return Catalog(**result)

    def update_catalog(self, catalog_id: UUID, catalog_update: CatalogUpdate) -> Optional[Catalog]:
        """Update a catalog entry."""
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
            return Catalog(**result)
        
        return None

    def delete_catalog(self, catalog_id: UUID) -> bool:
        """Delete a catalog entry."""
        return self.db.delete_catalog(str(catalog_id))

    def search_catalogs(self, tags: Optional[List[str]] = None, query: Optional[str] = None) -> List[Catalog]:
        """Search catalogs by tags and/or full-text search."""
        results = self.db.search_catalogs(tags, query)
        
        # Convert to Catalog models
        catalogs = []
        for result in results:
            # Convert string URLs to HttpUrl objects
            result["url"] = HttpUrl(result["url"])
            result["locations"] = [HttpUrl(loc) for loc in result["locations"]]
            catalogs.append(Catalog(**result))
        
        return catalogs