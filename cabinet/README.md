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

- POST /{org_name}/{group_name}/{user_name}/ - Create a new catalog
- POST /{org_name}/{group_name}/{user_name}/new - Create a new catalog from a Markdown file upload
- GET /{org_name}/{group_name}/{user_name}/{catalog_id} - Get a catalog by ID
- PUT /{org_name}/{group_name}/{user_name}/{catalog_id} - Update a catalog
- DELETE /{org_name}/{group_name}/{user_name}/{catalog_id} - Delete a catalog

### Search

- GET /{org_name}/{group_name}/{user_name}/search/?tag=tag1,tag2 - Search by tags
- GET /{org_name}/{group_name}/{user_name}/search/?q=searchterm - Full-text search
- GET /{org_name}/{group_name}/{user_name}/search/?tag=tag1&q=searchterm - Combined search


### Markdown File Upload

You can upload Markdown files directly to create new catalog entries using the `/catalogs/new` endpoint.
The Markdown file should include YAML frontmatter with the following metadata fields:

```markdown
---
title: data1.csv # Title
author: b@contoso.com # Author's email address
url: https://contoso.com/data1.md # Location of the catalog markdown file
tags: [sample, csv] # Tags
locations: [https://contoso.com/data1.csv] # Locations of the data, multiple possible
created_at: 2025-01-01T12:34:56Z # Creation date (optional)
updated_at: 2025-05-20T12:34:56Z # Last update date (optional)
---
# data1.csv

This data is...
```

You can provide the Markdown content in one of two ways:

1. As a multipart/form-data upload with a file field
2. By sending the Markdown content directly with Content-Type: text/markdown

The endpoint will parse the frontmatter metadata and create a catalog entry with the appropriate fields.

## Database Structure

DuckDB is used with the following structure:

- **Database**: Corresponds to an Organization (`org_name`)
- **Schema**: Corresponds to a Group (`group_name`)
- **Table**: Corresponds to a User (`user_name`)
- **Record**: Corresponds to a Markdown catalog file

### Table Definition

```sql
-- filepath: /Users/tesshy/Library/CloudStorage/SynologyDrive-tesshy/team-7.org/Developments/catalyzer/cabinet/README.md
CREATE SCHEMA IF NOT EXISTS {group_name};

CREATE TABLE IF NOT EXISTS {group_name}.{user_name} (
    id UUID PRIMARY KEY,
    title VARCHAR,
    author VARCHAR,
    url VARCHAR,
    tags VARCHAR[],
    locations VARCHAR[],
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    content VARCHAR,
    properties JSON
);
```

The `properties` field stores the complete YAML frontmatter as JSON, allowing you to access all metadata from the original markdown file, even custom fields that are not part of the standard schema.