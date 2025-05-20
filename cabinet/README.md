# Catalyzer::Cabinet

Catalyzer::Cabinet is a backend service for cataloging data files in a datalake using markdown files.

## Features

- Catalog management (CRUD operations for markdown catalogs)
- Search functionality (tag-based and full-text)
- DuckDB integration for efficient storage and retrieval

## Requirements

- Python 3.12
- FastAPI
- DuckDB

## Getting Started

### Installation

```bash
# Navigate to the cabinet directory
cd cabinet

# Install dependencies
pip install -r requirements.txt
```

### Running the Service

```bash
# Start the FastAPI server
uvicorn cabinet.main:app --reload
```

The API will be available at http://localhost:8000

### API Documentation

Once the service is running, you can access the auto-generated API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Catalog Format

Catalogs are represented as Markdown files with YAML frontmatter:

```markdown
---
title: data1.csv # Title
author: b@contoso.com # Author's email address
url: https://contoso.com/data1.md # Location of the catalog markdown file
tags: [sample, csv] # Tags
locations: ["https://contoso.com/data1.csv" ] # Locations of the data, multiple possible
created_at: 2025-01-01T12:34:56Z # Creation date
updated_at: 2025-05-20T12:34:56Z # Last update date   
---
# data1.csv

This data is...
```

## API Endpoints

### Catalog Management

- `POST /catalogs/` - Create a new catalog
- `GET /catalogs/{catalog_id}` - Get a catalog by ID
- `PUT /catalogs/{catalog_id}` - Update a catalog
- `DELETE /catalogs/{catalog_id}` - Delete a catalog

### Search

- `GET /catalogs/search/?tag=tag1,tag2` - Search by tags
- `GET /catalogs/search/?q=searchterm` - Full-text search
- `GET /catalogs/search/?tag=tag1&q=searchterm` - Combined search

## Database Structure

DuckDB is used with the following structure:

- **Database**: Corresponds to a Group (e.g., department)
- **Table**: Corresponds to a User (e.g., UUID)
- **Record**: Corresponds to a Markdown catalog file

### Table Definition

```sql
CREATE TABLE IF NOT EXISTS cabinet (
    id UUID PRIMARY KEY,
    title VARCHAR,
    author VARCHAR,
    url VARCHAR,
    tags VARCHAR[],
    locations VARCHAR[],
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    content VARCHAR
);
```