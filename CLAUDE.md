# CLAUDE.md

- 開発者は日本人なので、なるべく日本語でやりとりするようにしてください
- 現在開発を進めているのは、/cabinet ディレクトリ以下のFastAPIアプリケーションです。
- This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.


## Project Overview

Catalyzer is a FastAPI-based catalog system for datalakes that manages data assets using Markdown files with YAML frontmatter. It provides a REST API for creating, searching, and managing "catalogs" (目録) - structured documentation for data files.

## Development Commands

```bash
# Navigate to the main application directory
cd cabinet/

# Install dependencies
uv sync
# OR
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload

# Run all tests
pytest

# Run specific test file
pytest app/tests/test_catalog_service.py

# Run tests with verbose output
pytest -v

# API documentation available at:
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

## Architecture

### API Structure
The REST API follows a hierarchical path structure: `/{org_name}/{group_name}/{user_name}/`
- Database = Organization (`org_name`)
- Schema = Group (`group_name`) 
- Table = User (`user_name`)
- Records = Individual catalog entries

### Key Components
- **Models** (`app/models/catalog.py`): Pydantic data models for validation
- **Services** (`app/services/`): Business logic layer separated from API routes
- **Routers** (`app/routers/catalogs.py`): FastAPI route handlers
- **Database** (`app/database.py`): DuckDB operations with CabinetDB class

### Database
Uses DuckDB with optional MotherDuck cloud support (set `motherduck_token` environment variable). Database files are stored in `_data/cabinet.duckdb` (development) and `data/cabinet.duckdb` (production).

### Testing
- Uses pytest with FastAPI TestClient
- `conftest.py` provides shared fixtures and automatic database setup/teardown
- Tests are organized by component (service tests, API tests, etc.)

### Catalog Data Format
Catalogs are stored with YAML frontmatter containing metadata (title, author, url, tags, locations, timestamps) and optional markdown content for descriptions.

## Development Patterns

- Use dependency injection for database connections via FastAPI
- Follow the service layer pattern - keep business logic in `services/`, not in route handlers
- All database operations go through the `CabinetDB` class
- Use Pydantic models for request/response validation
- Maintain the hierarchical organization structure (org/group/user) in all API endpoints