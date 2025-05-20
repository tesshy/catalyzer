"""API routes for catalog operations."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..models import Catalog, CatalogCreate, CatalogUpdate, SearchQuery
from ..services.catalog_service import CatalogService

router = APIRouter(
    prefix="/catalogs",
    tags=["catalogs"],
)


@router.post("/", response_model=Catalog, status_code=status.HTTP_201_CREATED)
async def create_catalog(
    catalog: CatalogCreate,
    catalog_service: CatalogService = Depends(),
):
    """Create a new catalog entry."""
    return catalog_service.create_catalog(catalog)


@router.get("/{catalog_id}", response_model=Catalog)
async def get_catalog(
    catalog_id: UUID,
    catalog_service: CatalogService = Depends(),
):
    """Get a specific catalog entry."""
    catalog = catalog_service.get_catalog(catalog_id)
    if not catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Catalog with ID {catalog_id} not found",
        )
    return catalog


@router.put("/{catalog_id}", response_model=Catalog)
async def update_catalog(
    catalog_id: UUID,
    catalog_update: CatalogUpdate,
    catalog_service: CatalogService = Depends(),
):
    """Update a catalog entry."""
    catalog = catalog_service.update_catalog(catalog_id, catalog_update)
    if not catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Catalog with ID {catalog_id} not found",
        )
    return catalog


@router.delete("/{catalog_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_catalog(
    catalog_id: UUID,
    catalog_service: CatalogService = Depends(),
):
    """Delete a catalog entry."""
    deleted = catalog_service.delete_catalog(catalog_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Catalog with ID {catalog_id} not found",
        )


@router.get("/search/", response_model=List[Catalog])
async def search_catalogs(
    tag: Optional[List[str]] = Query(None),
    q: Optional[str] = Query(None),
    catalog_service: CatalogService = Depends(),
):
    """Search for catalogs by tags and/or full-text search."""
    if not tag and not q:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one search parameter (tag or q) is required",
        )
    
    return catalog_service.search_catalogs(tags=tag, query=q)