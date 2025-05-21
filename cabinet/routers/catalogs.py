"""API routes for catalog operations."""

import re
import yaml
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status, UploadFile, File
from pydantic import HttpUrl

from ..models import Catalog, CatalogCreate, CatalogUpdate, SearchQuery
from ..services.catalog_service import CatalogService


# Create a router with explicit routes that don't interfere with dynamic paths
router = APIRouter(
    prefix="/catalogs",
    tags=["catalogs"],
)


@router.get("/", response_model=List[Catalog])
async def list_catalogs(
    catalog_service: CatalogService = Depends(),
):
    """List all catalog entries."""
    return catalog_service.search_catalogs()


@router.post("/", response_model=Catalog, status_code=status.HTTP_201_CREATED)
async def create_catalog(
    catalog: CatalogCreate,
    catalog_service: CatalogService = Depends(),
):
    """Create a new catalog entry."""
    return catalog_service.create_catalog(catalog)


@router.get("/catalogs/search", response_model=List[Catalog])
async def search_catalogs_full_path(
    tag: Optional[List[str]] = Query(None),
    q: Optional[str] = Query(None),
    catalog_service: CatalogService = Depends(),
):
    """Search for catalogs by tags and/or full-text search (full path)."""
    if not tag and not q:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one search parameter (tag or q) is required",
        )
    
    return catalog_service.search_catalogs(tags=tag, query=q)


@router.get("/search", response_model=List[Catalog])
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


@router.post("/new", response_model=Catalog, status_code=status.HTTP_201_CREATED)
async def upload_markdown(
    request: Request,
    catalog_service: CatalogService = Depends(),
):
    """Create a new catalog entry from direct text/markdown content."""
    markdown_content = None
    filename = "document.md"
    
    # Handle direct text/markdown content
    if request.headers.get("content-type") == "text/markdown":
        content = await request.body()
        try:
            markdown_content = content.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Markdown content must be UTF-8 encoded",
            )
    
    # Content-Type is not text/markdown
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content-Type must be text/markdown",
        )
    
    try:
        # Use the catalog service to create from markdown
        return catalog_service.create_catalog_from_markdown(markdown_content, filename)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to parse markdown: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create catalog: {str(e)}",
        )


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