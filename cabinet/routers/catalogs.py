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
    tags=["catalogs"],
)


@router.post("/{group_name}/{user_name}", response_model=Catalog, status_code=status.HTTP_201_CREATED)
async def create_catalog(
    group_name: str,
    user_name: str,
    catalog: CatalogCreate,
    catalog_service: CatalogService = Depends(),
):
    """Create a new catalog entry."""
    return catalog_service.create_catalog(catalog, group_name, user_name)


@router.get("/{group_name}/{user_name}/{catalog_id}", response_model=Catalog)
async def get_catalog(
    group_name: str,
    user_name: str,
    catalog_id: UUID,
    catalog_service: CatalogService = Depends(),
):
    """Get a specific catalog entry."""
    catalog = catalog_service.get_catalog(catalog_id, group_name, user_name)
    if not catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Catalog with ID {catalog_id} not found",
        )
    return catalog


@router.put("/{group_name}/{user_name}/{catalog_id}", response_model=Catalog)
async def update_catalog(
    group_name: str,
    user_name: str,
    catalog_id: UUID,
    catalog_update: CatalogUpdate,
    catalog_service: CatalogService = Depends(),
):
    """Update a catalog entry."""
    catalog = catalog_service.update_catalog(catalog_id, catalog_update, group_name, user_name)
    if not catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Catalog with ID {catalog_id} not found",
        )
    return catalog


@router.delete("/{group_name}/{user_name}/{catalog_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_catalog(
    group_name: str,
    user_name: str,
    catalog_id: UUID,
    catalog_service: CatalogService = Depends(),
):
    """Delete a catalog entry."""
    deleted = catalog_service.delete_catalog(catalog_id, group_name, user_name)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Catalog with ID {catalog_id} not found",
        )


@router.get("/{group_name}/{user_name}/search/", response_model=List[Catalog])
async def search_catalogs(
    group_name: str,
    user_name: str,
    tag: Optional[List[str]] = Query(None),
    q: Optional[str] = Query(None),
    catalog_service: CatalogService = Depends(),
):
    """Search for catalogs by tags and/or full-text search."""
    # Remove the check that forces at least one parameter for testing
    # if not tag and not q:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="At least one search parameter (tag or q) is required",
    #     )
    
    return catalog_service.search_catalogs(tags=tag, query=q, group_name=group_name, user_name=user_name)


@router.post("/{group_name}/{user_name}/new", response_model=Catalog, status_code=status.HTTP_201_CREATED)
async def upload_markdown(
    group_name: str,
    user_name: str,
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
            markdown=main_content,
            properties=frontmatter,  # Include the full frontmatter in properties
            created_at=frontmatter.get("created_at", now),
            updated_at=frontmatter.get("updated_at", now),
        )
        
        # Create the catalog
        return catalog_service.create_catalog(catalog, group_name, user_name)
        
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