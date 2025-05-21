from fastapi import (
    FastAPI, Depends, Path, HTTPException, Body, File, UploadFile, Form, Request, status
)
from duckdb import DuckDBPyConnection # For type hinting
from typing import AsyncGenerator, Dict, Any, List, Optional, Tuple
import os # For uvicorn example and MOTHERDUCK_TOKEN check
import uuid # For UUID generation
from uuid import UUID as PyUUID # For type hinting UUID objects
from datetime import datetime, timezone
import yaml # For parsing frontmatter
import json # For handling JSON properties

# Import Pydantic models
from cabinet.models import CatalogItem, CatalogItemCreate

# Import the actual database connection function from database.py
# Ensure cabinet.database is resolvable. If running main.py directly for testing, PYTHONPATH might need adjustment.
from cabinet.database import get_db_connection as get_actual_db_connection

app = FastAPI(
    title="Cabinet API",
    description="API for managing catalog items in a DuckDB database (local or MotherDuck). CRUD operations.",
    version="0.1.0",
)

# Dependency to get a database connection
async def get_db(
    group_name: str = Path(..., title="Group Name", description="The name of the group (database/schema)."),
    user_name: str = Path(..., title="User Name", description="The name of the user (table name). Valid table name.")
) -> AsyncGenerator[DuckDBPyConnection, None]:
    """
    FastAPI dependency to get a DuckDB connection. Ensures table and schema exist.
    Ensures the connection is closed after the request.
    The connection is specific to the group_name (schema) and user_name (table).
    """
    connection: DuckDBPyConnection | None = None
    try:
        # Validate user_name to prevent SQL injection issues with table names
        # A simple check: ensure it's alphanumeric + underscores.
        # More robust validation might be needed depending on allowed table name characters.
        if not user_name.replace('_', '').isalnum():
            raise ValueError("Invalid user_name format. Must be alphanumeric with underscores.")
        connection = get_actual_db_connection(group_name, user_name)
        yield connection
    except ValueError as ve: # Catch specific validation error for user_name
        raise HTTPException(status_code=400, detail=f"Invalid table name: {str(ve)}")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed for group '{group_name}', user '{user_name}': {str(e)}")
    finally:
        if connection:
            connection.close()

# --- Helper Functions ---

def _db_row_to_catalog_item(row: Tuple, columns: List[str]) -> Optional[CatalogItem]:
    """Converts a database row tuple to a CatalogItem Pydantic model."""
    if not row:
        return None
    row_dict = dict(zip(columns, row))
    # Ensure complex types are correctly formatted if needed (e.g., JSON strings to dicts)
    # DuckDB driver usually handles this for basic types, UUIDs, and datetimes.
    # Tags and locations are lists of strings. Properties is a dict.
    if 'properties' in row_dict and isinstance(row_dict['properties'], str):
        try:
            row_dict['properties'] = json.loads(row_dict['properties'])
        except json.JSONDecodeError:
            # Keep as string if not valid JSON, or handle error
            pass # Or log a warning
    return CatalogItem.model_validate(row_dict)

def parse_markdown_with_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
    """Parses YAML frontmatter and content from a markdown string."""
    frontmatter = {}
    markdown_content = content
    try:
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3: # Found frontmatter
                frontmatter_str = parts[1]
                markdown_content = parts[2].lstrip() # Remove leading whitespace
                frontmatter = yaml.safe_load(frontmatter_str)
                if not isinstance(frontmatter, dict): # Handle non-dict frontmatter
                    frontmatter = {"raw_frontmatter": frontmatter}
    except yaml.YAMLError:
        # If YAML parsing fails, treat the whole thing as markdown content
        # or raise an error. For now, just use empty frontmatter.
        frontmatter = {"parsing_error": "YAML frontmatter could not be parsed."}
        markdown_content = content # Reassign full content if parsing fails
    except Exception:
        # Catch any other unexpected errors during parsing
        frontmatter = {"parsing_error": "An unexpected error occurred during frontmatter parsing."}
        markdown_content = content
        
    return frontmatter, markdown_content

# --- API Endpoints ---

@app.get("/", tags=["General"])
async def read_root() -> Dict[str, str]:
    """Root endpoint to check if the API is running."""
    return {"message": "Catalyzer::Cabinet is running!"}

# 1. Create new catalog item from JSON
@app.post("/{group_name}/{user_name}/", response_model=CatalogItem, status_code=status.HTTP_201_CREATED, tags=["Catalog"])
async def create_catalog_item_json(
    item_data: CatalogItemCreate,
    group_name: str = Path(...),
    user_name: str = Path(...),
    db: DuckDBPyConnection = Depends(get_db)
):
    item_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    # Handle optional fields for insertion
    tags_to_insert = item_data.tags if item_data.tags is not None else []
    locations_to_insert = item_data.locations if item_data.locations is not None else []
    properties_to_insert = json.dumps(item_data.properties) if item_data.properties is not None else None
    markdown_to_insert = item_data.markdown if item_data.markdown is not None else ""


    insert_query = f"""
    INSERT INTO {user_name} (id, title, author, url, tags, locations, created_at, updated_at, markdown, properties)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    try:
        db.execute(
            insert_query,
            [
                item_id,
                item_data.title,
                item_data.author,
                item_data.url,
                tags_to_insert,
                locations_to_insert,
                item_data.created_at or now, # Use provided or default to now
                item_data.updated_at or now, # Use provided or default to now
                markdown_to_insert,
                properties_to_insert,
            ],
        )
        # Fetch the newly created item
        # Note: Table name user_name is sanitized by get_db dependency somewhat
        select_query = f"SELECT id, title, author, url, tags, locations, created_at, updated_at, markdown, properties FROM {user_name} WHERE id = ?"
        created_item_row = db.execute(select_query, [item_id]).fetchone()
        
        if not created_item_row:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create or retrieve catalog item.")

        columns = [desc[0] for desc in db.description]
        return _db_row_to_catalog_item(created_item_row, columns)

    except duckdb.Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error processing request: {str(e)}")


# 2. Create new catalog item from Markdown
@app.post("/{group_name}/{user_name}/new", response_model=CatalogItem, status_code=status.HTTP_201_CREATED, tags=["Catalog"])
async def create_catalog_item_markdown(
    request: Request,
    group_name: str = Path(...),
    user_name: str = Path(...),
    file: Optional[UploadFile] = File(None), # For multipart/form-data
    # For text/markdown, we'll read the body directly if 'file' is not provided.
    # Using Optional[str] = Body(None) for raw body is tricky with File.
    # Instead, we check content_type and read request.body()
    db: DuckDBPyConnection = Depends(get_db)
):
    content_type = request.headers.get("content-type", "")
    markdown_str_content: str = ""

    if file: # multipart/form-data
        if not file.content_type or "markdown" not in file.content_type.lower():
             # Stricter check could be file.content_type == "text/markdown"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type. Please upload a Markdown file.")
        file_content_bytes = await file.read()
        markdown_str_content = file_content_bytes.decode("utf-8")
        await file.close()
    elif "text/markdown" in content_type: # text/markdown
        body_bytes = await request.body()
        markdown_str_content = body_bytes.decode("utf-8")
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported Content-Type. Use multipart/form-data with a file or text/markdown.")

    if not markdown_str_content.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Markdown content cannot be empty.")

    frontmatter, md_content_body = parse_markdown_with_frontmatter(markdown_str_content)

    if "parsing_error" in frontmatter:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error parsing frontmatter: {frontmatter['parsing_error']}")
    if not frontmatter.get("title") or not frontmatter.get("author") or not frontmatter.get("url"):
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required frontmatter fields: title, author, url.")

    item_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    # Extract standard fields, allowing for missing ones (Pydantic model will handle defaults if any)
    title = frontmatter.get("title", "Untitled")
    author = frontmatter.get("author", "Unknown Author")
    url = frontmatter.get("url", "")
    tags = frontmatter.get("tags", [])
    locations = frontmatter.get("locations", [])
    
    # Handle created_at and updated_at from frontmatter
    # PyYAML might parse dates as Python datetime objects or strings.
    def parse_datetime_flexible(dt_val):
        if isinstance(dt_val, datetime):
            return dt_val.astimezone(timezone.utc) if dt_val.tzinfo else dt_val.replace(tzinfo=timezone.utc)
        if isinstance(dt_val, str):
            try:
                # Attempt to parse ISO format string
                dt_obj = datetime.fromisoformat(dt_val.replace("Z", "+00:00"))
                return dt_obj.astimezone(timezone.utc) if dt_obj.tzinfo else dt_obj.replace(tzinfo=timezone.utc)
            except ValueError:
                return now # Default if parsing fails
        return now # Default for other types or None

    created_at_fm = frontmatter.get("created_at")
    updated_at_fm = frontmatter.get("updated_at")

    created_at = parse_datetime_flexible(created_at_fm) if created_at_fm else now
    updated_at = parse_datetime_flexible(updated_at_fm) if updated_at_fm else now
    
    # The entire frontmatter (including custom fields) goes into 'properties'
    properties_json = json.dumps(frontmatter)

    insert_query = f"""
    INSERT INTO {user_name} (id, title, author, url, tags, locations, created_at, updated_at, markdown, properties)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    try:
        db.execute(insert_query, [
            item_id, title, author, url, tags, locations, created_at, updated_at, md_content_body, properties_json
        ])
        
        select_query = f"SELECT id, title, author, url, tags, locations, created_at, updated_at, markdown, properties FROM {user_name} WHERE id = ?"
        created_item_row = db.execute(select_query, [item_id]).fetchone()
        if not created_item_row:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve catalog item after creation from Markdown.")
        
        columns = [desc[0] for desc in db.description]
        return _db_row_to_catalog_item(created_item_row, columns)

    except duckdb.Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error on Markdown creation: {str(e)}")
    except Exception as e:
        # Catch-all for other errors during processing
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error processing Markdown request: {str(e)}")


# 3. Get catalog item by ID
@app.get("/{group_name}/{user_name}/{catalog_id}", response_model=CatalogItem, tags=["Catalog"])
async def get_catalog_item(
    catalog_id: PyUUID, # FastAPI handles string to UUID conversion
    group_name: str = Path(...),
    user_name: str = Path(...),
    db: DuckDBPyConnection = Depends(get_db)
):
    query = f"SELECT id, title, author, url, tags, locations, created_at, updated_at, markdown, properties FROM {user_name} WHERE id = ?"
    try:
        item_row = db.execute(query, [catalog_id]).fetchone()
        if not item_row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalog item not found")
        
        columns = [desc[0] for desc in db.description] # Get column names from the query result
        return _db_row_to_catalog_item(item_row, columns)
    except duckdb.Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database query error: {str(e)}")


# 4. Update catalog item
@app.put("/{group_name}/{user_name}/{catalog_id}", response_model=CatalogItem, tags=["Catalog"])
async def update_catalog_item(
    catalog_id: PyUUID,
    item_update_data: CatalogItemCreate, # Re-use CatalogItemCreate for update payload
    group_name: str = Path(...),
    user_name: str = Path(...),
    db: DuckDBPyConnection = Depends(get_db)
):
    # First, check if item exists
    check_query = f"SELECT id FROM {user_name} WHERE id = ?"
    existing_item = db.execute(check_query, [catalog_id]).fetchone()
    if not existing_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalog item not found for update.")

    now = datetime.now(timezone.utc)
    
    # Build the SET part of the query dynamically
    update_fields = item_update_data.model_dump(exclude_unset=True) # Only fields present in payload
    set_clauses = []
    params = []

    for key, value in update_fields.items():
        if value is not None: # Ensure not to set fields to NULL if not intended
            set_clauses.append(f"{key} = ?")
            if key == "properties" and isinstance(value, dict):
                params.append(json.dumps(value))
            elif key == "tags" or key == "locations" and not isinstance(value, list):
                 # Ensure lists are passed as lists if they are not. This might be redundant with Pydantic.
                params.append(list(value) if value is not None else [])
            else:
                params.append(value)
    
    if not set_clauses: # Nothing to update if all values in payload were None or empty
        # Or, fetch and return current item if no actual changes
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update or all fields are null.")

    set_clauses.append("updated_at = ?")
    params.append(now)
    
    update_query = f"UPDATE {user_name} SET {', '.join(set_clauses)} WHERE id = ?"
    params.append(catalog_id)
    
    try:
        db.execute(update_query, params)
        
        # Fetch and return the updated item
        select_query = f"SELECT id, title, author, url, tags, locations, created_at, updated_at, markdown, properties FROM {user_name} WHERE id = ?"
        updated_item_row = db.execute(select_query, [catalog_id]).fetchone()
        if not updated_item_row: # Should not happen if update was successful on existing ID
             raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve item after update.")

        columns = [desc[0] for desc in db.description]
        return _db_row_to_catalog_item(updated_item_row, columns)

    except duckdb.Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error during update: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error processing update request: {str(e)}")


# 5. Delete catalog item
@app.delete("/{group_name}/{user_name}/{catalog_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Catalog"])
async def delete_catalog_item(
    catalog_id: PyUUID,
    group_name: str = Path(...),
    user_name: str = Path(...),
    db: DuckDBPyConnection = Depends(get_db)
):
    # Check if item exists before deleting (optional, but good for 404)
    check_query = f"SELECT id FROM {user_name} WHERE id = ?"
    existing_item = db.execute(check_query, [catalog_id]).fetchone()
    if not existing_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalog item not found for deletion.")

    delete_query = f"DELETE FROM {user_name} WHERE id = ?"
    try:
        db.execute(delete_query, [catalog_id])
        # If execute() doesn't raise an error, and the item was confirmed to exist (by check_query),
        # the deletion is considered successful.
        # For HTTP 204, no response body should be sent.
        # FastAPI handles this correctly if the function returns None or nothing.
        return
    except duckdb.Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error during deletion: {str(e)}")


# Test endpoint (already present, can be kept or removed)
@app.get("/_test_db/{group_name}/{user_name}/status", tags=["Testing"])
async def test_db_connection(
    group_name: str = Path(..., description="Group name for testing"),
    user_name: str = Path(..., description="User name for testing"),
    db: DuckDBPyConnection = Depends(get_db)
) -> Dict[str, Any]:
    """
    Tests the database connection for a given group and user.
    This will create the DB/table if it doesn't exist via get_db -> get_actual_db_connection.
    """
    try:
        count_result = db.execute(f"SELECT COUNT(*) FROM {user_name};").fetchone()
        return {
            "message": "Database connection successful and table is accessible.",
            "group_name": group_name,
            "user_name": user_name,
            "table_exists_and_queriable": True,
            "item_count_in_table": count_result[0] if count_result else "N/A"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying table '{user_name}' in group '{group_name}': {str(e)}")

# 6. Search catalog items
@app.get("/{group_name}/{user_name}/search/", response_model=List[CatalogItem], tags=["Catalog"])
async def search_catalog_items(
    group_name: str = Path(...),
    user_name: str = Path(...),
    tag: Optional[List[str]] = Query(None, description="Tags to search for (e.g., tag1,tag2). Matches items containing ALL specified tags."),
    q: Optional[str] = Query(None, min_length=1, description="Full-text search term for title and markdown content."),
    db: DuckDBPyConnection = Depends(get_db)
):
    base_query = f"SELECT id, title, author, url, tags, locations, created_at, updated_at, markdown, properties FROM {user_name}"
    conditions = []
    params = []

    if tag:
        # Ensure 'tag' is a list, even if a single tag is passed via Query
        # FastAPI handles comma-separated values into a List[str] automatically for Query(None)
        for t in tag:
            if t.strip(): # Ensure tag is not empty string
                conditions.append("list_contains(tags, ?)") # DuckDB uses list_contains for arrays
                params.append(t.strip())
    
    if q and q.strip():
        # Case-insensitive LIKE search for title and markdown
        # For properties (JSON), a simple LIKE search is not effective. Requires JSON functions or FTS.
        # Sticking to title and markdown as per baseline requirement.
        q_lower = f"%{q.strip().lower()}%"
        conditions.append("(lower(title) LIKE ? OR lower(markdown) LIKE ?)")
        params.append(q_lower)
        params.append(q_lower)

    query = base_query
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY updated_at DESC;" # Default ordering

    try:
        results = db.execute(query, params).fetchall()
        if not results:
            return []
        
        columns = [desc[0] for desc in db.description]
        return [_db_row_to_catalog_item(row, columns) for row in results if row]
    except duckdb.Error as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database search error: {str(e)}")
    except Exception as e: # Catch any other unexpected error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred during search: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    print("Starting Uvicorn server for local development...")
    print("Access API docs at http://127.0.0.1:8000/docs")
    print("CRUD endpoints available under /{group_name}/{user_name}/")
    # Example: http://127.0.0.1:8000/docs
    # To run: python -m uvicorn cabinet.main:app --reload
    
    # Ensure cabinet.database and cabinet.models are importable if running directly
    # e.g., by setting PYTHONPATH=. when in the parent directory of 'cabinet'
    # or running as `python -m cabinet.main` from parent directory (uvicorn handles this better)
    uvicorn.run("cabinet.main:app", host="127.0.0.1", port=8000, reload=True)