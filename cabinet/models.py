from uuid import UUID, uuid4
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class CatalogItemCreate(BaseModel):
    title: str
    author: str
    url: str
    tags: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    markdown: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    # For creation, these can be None and will be set by the server if not provided
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

class CatalogItem(CatalogItemCreate):
    id: UUID
    # In the retrieved item, these are not optional and are set by the database/server
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True # For Pydantic v2
        # orm_mode = True # For Pydantic v1

if __name__ == '__main__':
    # Example Usage and basic tests

    # Test CatalogItemCreate
    print("Testing CatalogItemCreate...")
    item_create_data_full = {
        "title": "The Hitchhiker's Guide to the Galaxy",
        "author": "Douglas Adams",
        "url": "https://example.com/hitchhikers",
        "tags": ["sci-fi", "comedy"],
        "locations": ["shelf1", "/digital/ebooks"],
        "markdown": "# Chapter 1\nDon't panic.",
        "properties": {"rating": 5, "read_status": "completed"}
    }
    item_create_obj_full = CatalogItemCreate(**item_create_data_full)
    assert item_create_obj_full.title == "The Hitchhiker's Guide to the Galaxy"
    assert item_create_obj_full.tags == ["sci-fi", "comedy"]
    assert item_create_obj_full.created_at is not None # Should have a default value
    print("CatalogItemCreate with full data: PASS")

    item_create_data_minimal = {
        "title": "Dune",
        "author": "Frank Herbert",
        "url": "https://example.com/dune"
    }
    item_create_obj_minimal = CatalogItemCreate(**item_create_data_minimal)
    assert item_create_obj_minimal.title == "Dune"
    assert item_create_obj_minimal.tags is None
    assert item_create_obj_minimal.created_at is not None # Should have a default value
    print("CatalogItemCreate with minimal data: PASS")

    # Test CatalogItem
    print("\nTesting CatalogItem...")
    item_id = uuid4()
    now = datetime.utcnow()
    
    item_data_from_db = {
        "id": item_id,
        "title": "1984",
        "author": "George Orwell",
        "url": "https://example.com/1984",
        "tags": ["dystopian"],
        "locations": ["box2"],
        "markdown": "It was a bright cold day in April...",
        "properties": {"borrowed_by": "Alice"},
        "created_at": now,
        "updated_at": now
    }
    item_obj = CatalogItem(**item_data_from_db)
    assert item_obj.id == item_id
    assert item_obj.title == "1984"
    assert item_obj.created_at == now
    assert item_obj.updated_at == now
    assert item_obj.tags == ["dystopian"]
    print("CatalogItem creation from dict: PASS")

    # Test CatalogItem.from_orm (mocking an ORM object)
    class MockORMItem:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

    mock_orm_data = {
        "id": uuid4(),
        "title": "Brave New World",
        "author": "Aldous Huxley",
        "url": "https://example.com/bravenewworld",
        "tags": ["sci-fi", "dystopian"],
        "locations": ["shelf3"],
        "markdown": None,
        "properties": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    mock_orm_instance = MockORMItem(**mock_orm_data)
    
    try:
        item_from_orm = CatalogItem.model_validate(mock_orm_instance) # Pydantic v2
        # item_from_orm = CatalogItem.from_orm(mock_orm_instance) # Pydantic v1
        assert item_from_orm.id == mock_orm_instance.id
        assert item_from_orm.title == "Brave New World"
        assert item_from_orm.tags == ["sci-fi", "dystopian"]
        print("CatalogItem.from_attributes (model_validate): PASS")
    except Exception as e:
        print(f"Error during from_attributes/model_validate test: {e}")
        # Fallback for Pydantic v1 if model_validate is not found (though Config specifies from_attributes for v2)
        try:
            print("Attempting with from_orm for Pydantic v1 compatibility...")
            item_from_orm_v1 = CatalogItem.from_orm(mock_orm_instance)
            assert item_from_orm_v1.id == mock_orm_instance.id
            assert item_from_orm_v1.title == "Brave New World"
            print("CatalogItem.from_orm (Pydantic v1 style): PASS")
        except Exception as e_v1:
            print(f"CatalogItem.from_orm (Pydantic v1 style) also failed: {e_v1}")


    print("\nAll model tests completed.")
