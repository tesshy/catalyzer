"""Data models for Catalyzer::Cabinet."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, HttpUrl


class CatalogBase(BaseModel):
    """Base model for catalog entries."""

    title: str
    author: str
    url: HttpUrl
    tags: List[str] = Field(default_factory=list)
    locations: List[HttpUrl] = Field(default_factory=list)
    content: str
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CatalogCreate(CatalogBase):
    """Model for creating a catalog entry."""

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CatalogUpdate(BaseModel):
    """Model for updating a catalog entry."""

    title: Optional[str] = None
    author: Optional[str] = None
    url: Optional[HttpUrl] = None
    tags: Optional[List[str]] = None
    locations: Optional[List[HttpUrl]] = None
    content: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None


class CatalogInDB(CatalogBase):
    """Model for a catalog entry in the database."""

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        orm_mode = True


class Catalog(CatalogInDB):
    """Model for a catalog entry response."""

    pass


class SearchQuery(BaseModel):
    """Model for search query parameters."""

    tag: Optional[List[str]] = None
    query: Optional[str] = None