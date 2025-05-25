"""Tests for vector search functionality."""

import pytest
from fastapi.testclient import TestClient
from uuid import UUID

from app.main import app
from app.database import CabinetDB
from app.services.catalog_service import CatalogService
from app.models.catalog import CatalogCreate
from pydantic import HttpUrl


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_catalog_data():
    """Sample catalog data for testing."""
    return {
        "title": "テストデータベース",
        "author": "テスト太郎", 
        "url": "https://example.com/test-db",
        "tags": ["データベース", "テスト"],
        "locations": ["https://example.com/data/test.db"],
        "markdown": "これはテスト用のデータベースです。日本語の文書を含んでいます。機械学習とデータ分析に使用されます。",
        "properties": {"type": "database", "format": "sqlite"}
    }


@pytest.fixture
def another_catalog_data():
    """Another sample catalog data for testing."""
    return {
        "title": "画像データセット",
        "author": "データサイエンティスト",
        "url": "https://example.com/images",
        "tags": ["画像", "AI"],
        "locations": ["https://example.com/data/images.zip"],
        "markdown": "画像認識のための大規模な画像データセットです。深層学習モデルの訓練に適しています。",
        "properties": {"type": "dataset", "format": "images"}
    }


class TestVectorSearch:
    """Test class for vector search functionality."""
    
    def test_catalog_with_vector_creation(self, db_connection, sample_catalog_data):
        """Test creating catalog with vector generation."""
        db = CabinetDB(db_connection)
        service = CatalogService(db)
        
        # Create catalog
        catalog_create = CatalogCreate(**sample_catalog_data)
        catalog = service.create_catalog("test_org", "test_user", catalog_create)
        
        # Check that vector was generated
        assert catalog.vector is not None
        assert len(catalog.vector) == 384
        assert any(x != 0.0 for x in catalog.vector)
    
    def test_catalog_update_regenerates_vector(self, db_connection, sample_catalog_data):
        """Test that updating markdown content regenerates vector."""
        from app.models.catalog import CatalogUpdate
        
        db = CabinetDB(db_connection)
        service = CatalogService(db)
        
        # Create catalog
        catalog_create = CatalogCreate(**sample_catalog_data)
        catalog = service.create_catalog("test_org", "test_user", catalog_create)
        original_vector = catalog.vector.copy()
        
        # Update markdown content
        update_data = CatalogUpdate(markdown="完全に異なる内容の文書です。新しいトピックについて説明しています。")
        updated_catalog = service.update_catalog("test_org", "test_user", catalog.id, update_data)
        
        # Check that vector was regenerated
        assert updated_catalog.vector is not None
        assert updated_catalog.vector != original_vector
    
    def test_vector_search_functionality(self, db_connection, sample_catalog_data, another_catalog_data):
        """Test vector search functionality."""
        db = CabinetDB(db_connection)
        service = CatalogService(db)
        
        # Create multiple catalogs
        catalog1 = service.create_catalog("test_org", "test_user", CatalogCreate(**sample_catalog_data))
        catalog2 = service.create_catalog("test_org", "test_user", CatalogCreate(**another_catalog_data))
        
        # Search for database-related content
        results = service.vector_search_catalogs("test_org", "test_user", "データベース", limit=10)
        
        # Should return results
        assert len(results) > 0
        
        # Results should be Catalog objects
        for result in results:
            assert hasattr(result, 'id')
            assert hasattr(result, 'title')
            assert hasattr(result, 'vector')
    
    def test_vector_search_with_japanese_query(self, db_connection, sample_catalog_data):
        """Test vector search with Japanese query."""
        db = CabinetDB(db_connection)
        service = CatalogService(db)
        
        # Create catalog
        service.create_catalog("test_org", "test_user", CatalogCreate(**sample_catalog_data))
        
        # Search with Japanese query
        results = service.vector_search_catalogs("test_org", "test_user", "機械学習", limit=5)
        
        # Should return results or empty list (depending on similarity)
        assert isinstance(results, list)
        
        # If results exist, they should be valid Catalog objects
        for result in results:
            assert hasattr(result, 'id')
            assert hasattr(result, 'markdown')
    
    def test_vector_search_empty_query(self, db_connection, sample_catalog_data):
        """Test vector search with empty query."""
        db = CabinetDB(db_connection)
        service = CatalogService(db)
        
        # Create catalog
        service.create_catalog("test_org", "test_user", CatalogCreate(**sample_catalog_data))
        
        # Search with empty query should fallback to regular search
        results = service.vector_search_catalogs("test_org", "test_user", "", limit=5)
        
        assert isinstance(results, list)
    
    def test_database_vector_search_method(self, db_connection, sample_catalog_data):
        """Test database-level vector search method."""
        db = CabinetDB(db_connection)
        
        # Create catalog with vector
        catalog_dict = sample_catalog_data.copy()
        catalog_dict["url"] = str(catalog_dict["url"])
        catalog_dict["locations"] = [str(loc) for loc in catalog_dict["locations"]]
        catalog_dict["vector"] = [0.1] * 384  # Mock vector
        
        db.create_catalog("test_org", "test_user", catalog_dict)
        
        # Test vector search
        query_vector = [0.1] * 384
        results = db.vector_search_catalogs("test_org", "test_user", query_vector, limit=5)
        
        assert isinstance(results, list)
        if results:  # If we have results
            assert 'vector' in results[0]
    
    def test_vector_search_no_vectors(self, db_connection):
        """Test vector search when no vectors exist."""
        db = CabinetDB(db_connection)
        
        # Create catalog without vector
        catalog_dict = {
            "title": "No Vector Catalog",
            "author": "Test",
            "url": "https://example.com",
            "tags": [],
            "locations": [],
            "markdown": "Test content",
            "properties": {}
        }
        
        db.create_catalog("test_org", "test_user", catalog_dict)
        
        # Test vector search
        query_vector = [0.1] * 384
        results = db.vector_search_catalogs("test_org", "test_user", query_vector, limit=5)
        
        # Should return empty list since no vectors exist
        assert isinstance(results, list)