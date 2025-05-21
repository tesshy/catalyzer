"""API routes for catalog operations."""

import re
import yaml
import io
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status, UploadFile, File, Form
from pydantic import HttpUrl

from markitdown import MarkItDown

from ..models import Catalog, CatalogCreate, CatalogUpdate, SearchQuery
from ..services.catalog_service import CatalogService


# Create a router without a prefix for specific paths
router = APIRouter(
    tags=["catalogs"],
)


@router.post("/{org_name}/{group_name}/{user_name}/", response_model=Catalog, status_code=status.HTTP_201_CREATED)
async def create_catalog(
    org_name: str,
    group_name: str,
    user_name: str,
    catalog: CatalogCreate,
    catalog_service: CatalogService = Depends(),
):
    """Create a new catalog entry."""
    return catalog_service.create_catalog(group_name, user_name, catalog)


@router.post("/{org_name}/{group_name}/{user_name}/new", response_model=Catalog, status_code=status.HTTP_201_CREATED)
async def upload_markdown(
    org_name: str,
    group_name: str,
    user_name: str,
    request: Request,
    file: Optional[UploadFile] = File(None),
    catalog_service: CatalogService = Depends(),
):
    """Create a new catalog entry from markdown file.
    
    Upload can be:
    1. A file upload with multipart/form-data
    2. Direct markdown content with content-type: text/markdown
    """
    markdown_content = None
    filename = "document.md"
    
    # Handle file upload
    if file:
        filename = file.filename
        markdown_content = await file.read()
        try:
            markdown_content = markdown_content.decode("utf-8")
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
            detail="Either a file upload or Content-Type: text/markdown is required",
        )
    
    try:
        # Use the catalog service to create from markdown
        return catalog_service.create_catalog_from_markdown(group_name, user_name, markdown_content, filename)
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


@router.get("/{org_name}/{group_name}/{user_name}/search", response_model=List[Catalog])
async def search_catalogs(
    org_name: str,
    group_name: str,
    user_name: str,
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
    
    return catalog_service.search_catalogs(group_name, user_name, tags=tag, query=q)


@router.get("/{org_name}/{group_name}/{user_name}/{catalog_id}", response_model=Catalog)
async def get_catalog(
    org_name: str,
    group_name: str,
    user_name: str,
    catalog_id: UUID,
    catalog_service: CatalogService = Depends(),
):
    """Get a specific catalog entry."""
    catalog = catalog_service.get_catalog(group_name, user_name, catalog_id)
    if not catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Catalog with ID {catalog_id} not found",
        )
    return catalog


@router.put("/{org_name}/{group_name}/{user_name}/{catalog_id}", response_model=Catalog)
async def update_catalog(
    org_name: str,
    group_name: str,
    user_name: str,
    catalog_id: UUID,
    catalog_update: CatalogUpdate,
    catalog_service: CatalogService = Depends(),
):
    """Update a catalog entry."""
    catalog = catalog_service.update_catalog(group_name, user_name, catalog_id, catalog_update)
    if not catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Catalog with ID {catalog_id} not found",
        )
    return catalog


@router.delete("/{org_name}/{group_name}/{user_name}/{catalog_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_catalog(
    org_name: str,
    group_name: str,
    user_name: str,
    catalog_id: UUID,
    catalog_service: CatalogService = Depends(),
):
    """Delete a catalog entry."""
    deleted = catalog_service.delete_catalog(group_name, user_name, catalog_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Catalog with ID {catalog_id} not found",
        )


@router.get("/", response_model=str)
async def generate_markdown_from_url(
    url: str = Query(..., description="URL to fetch content from"),
):
    """Generate a markdown catalog file from a URL.
    
    Uses markitdown to convert web content to markdown with front matter.
    
    Args:
        url: The URL to fetch and convert
        
    Returns:
        Markdown content with front matter
    
    Raises:
        HTTPException: If the URL is invalid or content cannot be converted
    """
    try:
        # Create a markitdown instance
        markitdown = MarkItDown()
        
        # Convert the URL to markdown
        result = markitdown.convert_url(url)
        
        # Extract title from the result or use URL as fallback
        title = result.title or url.split("/")[-1] or "Untitled"
        
        # Create front matter with required fields
        front_matter = {
            "title": title,
            "author": "",
            "url": url,
            "tags": [],
            "locations": [url],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        # Format the front matter as YAML
        front_matter_yaml = yaml.dump(front_matter, default_flow_style=False)
        
        # Combine front matter and markdown content
        markdown_with_front_matter = f"---\n{front_matter_yaml}---\n\n{result.markdown}"
        
        return markdown_with_front_matter
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to generate markdown from URL: {str(e)}",
        )