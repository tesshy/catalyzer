"""API routes for catalog operations."""

import re
import yaml
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status, UploadFile, File, Form
from pydantic import HttpUrl

from ..models import Catalog, CatalogCreate, CatalogUpdate, SearchQuery
from ..services.catalog_service import CatalogService


# Create a router without a prefix for specific paths
router = APIRouter(
    tags=["catalogs"],
)


@router.post("/{group_name}/{user_name}/", response_model=Catalog, status_code=status.HTTP_201_CREATED)
async def create_catalog(
    group_name: str,
    user_name: str,
    catalog: CatalogCreate,
    catalog_service: CatalogService = Depends(),
):
    """Create a new catalog entry."""
    return catalog_service.create_catalog(group_name, user_name, catalog)


@router.post("/{group_name}/{user_name}/new", response_model=Catalog, status_code=status.HTTP_201_CREATED)
async def upload_markdown(
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


@router.get("/{group_name}/{user_name}/search", response_model=List[Catalog])
async def search_catalogs(
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


@router.get("/{group_name}/{user_name}/{catalog_id}", response_model=Catalog)
async def get_catalog(
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


@router.put("/{group_name}/{user_name}/{catalog_id}", response_model=Catalog)
async def update_catalog(
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


@router.delete("/{group_name}/{user_name}/{catalog_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_catalog(
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