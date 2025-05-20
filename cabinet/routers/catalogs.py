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


@router.post("/new", response_model=Catalog, status_code=status.HTTP_201_CREATED)
async def upload_markdown(
    request: Request,
    file: UploadFile = File(None),
    catalog_service: CatalogService = Depends(),
):
    """Create a new catalog entry from a Markdown file upload or direct text/markdown content."""
    markdown_content = None
    filename = "document.md"
    
    # Handle file upload
    if file:
        if not file.filename.endswith((".md", ".markdown")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only Markdown files are accepted",
            )
            
        filename = file.filename
        content = await file.read()
        try:
            markdown_content = content.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Markdown file must be UTF-8 encoded",
            )
    
    # Handle direct text/markdown content
    elif request.headers.get("content-type") == "text/markdown":
        content = await request.body()
        try:
            markdown_content = content.decode("utf-8")
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Markdown content must be UTF-8 encoded",
            )
    
    # Neither file nor text/markdown content provided
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content-Type must be text/markdown when not using multipart/form-data",
        )
    
    # Process the markdown content
    try:
        # Extract YAML frontmatter using regex
        pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
        match = re.match(pattern, markdown_content, re.DOTALL)
        
        if not match:
            raise ValueError("Invalid markdown format: Missing frontmatter")
        
        frontmatter_str, main_content = match.groups()
        
        # Parse YAML frontmatter
        try:
            frontmatter = yaml.safe_load(frontmatter_str)
            if not isinstance(frontmatter, dict):
                raise ValueError("Frontmatter is not a dictionary")
        except Exception as e:
            raise ValueError(f"Failed to parse frontmatter: {str(e)}")
        
        # Create a new catalog directly
        now = datetime.now()
        
        # Create catalog data
        catalog = CatalogCreate(
            title=frontmatter.get("title", filename),
            author=frontmatter.get("author", ""),
            url=HttpUrl(frontmatter.get("url", "https://example.com/")),
            tags=frontmatter.get("tags", []),
            locations=[HttpUrl(location) for location in frontmatter.get("locations", [])],
            content=main_content,
            properties=frontmatter,  # Include the full frontmatter in properties
            created_at=frontmatter.get("created_at", now),
            updated_at=frontmatter.get("updated_at", now),
        )
        
        # Create the catalog
        return catalog_service.create_catalog(catalog)
        
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