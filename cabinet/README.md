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

#### Local Database (Default)

```bash
# Start the FastAPI server with local DuckDB storage
uvicorn cabinet.main:app --reload
```

#### MotherDuck Cloud Database

To use MotherDuck cloud database:

```bash
# Set your MotherDuck token as environment variable
export motherduck_token='your_motherduck_token'

# Start the FastAPI server
uvicorn cabinet.main:app --reload
```

When the `MOTHERDUCK_TOKEN` environment variable is present, the application will automatically connect to MotherDuck cloud instead of the local database file.

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

- `POST /{group_name}/{user_name}/` - Create a new catalog
- `POST /{group_name}/{user_name}/new` - Create a new catalog from a Markdown file upload
- `GET /{group_name}/{user_name}/{catalog_id}` - Get a catalog by ID
- `PUT /{group_name}/{user_name}/{catalog_id}` - Update a catalog
- `DELETE /{group_name}/{user_name}/{catalog_id}` - Delete a catalog

### Search

- `GET /{group_name}/{user_name}/search/?tag=tag1,tag2` - Search by tags
- `GET /{group_name}/{user_name}/search/?q=searchterm` - Full-text search
- `GET /{group_name}/{user_name}/search/?tag=tag1&q=searchterm` - Combined search

### Markdown File Upload

You can upload Markdown files directly to create new catalog entries using the `/{group_name}/{user_name}/new` endpoint.
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

The content after the frontmatter will be stored in the `markdown` field.

You can provide the Markdown content in one of two ways:

1. As a multipart/form-data upload with a file field
2. By sending the Markdown content directly with Content-Type: text/markdown

The endpoint will parse the frontmatter metadata and create a catalog entry with the appropriate fields.

## Database Structure

DuckDB is used with the following structure:

- **Database/Schema**: `{group_name}` - Corresponds to a Group (e.g., department)
- **Table**: `{user_name}` - Corresponds to a User (e.g., UUID)
- **Record**: Corresponds to a Markdown catalog file

### Storage Options

#### Local Storage (Default)
By default, the application uses local DuckDB file storage in the `cabinet/data` directory.

#### MotherDuck Cloud Storage
When the `MOTHERDUCK_TOKEN` environment variable is set, the application connects to MotherDuck cloud database:
- The `{group_name}` is used as the database name in MotherDuck
- Authentication is managed through the MotherDuck token
- All data is persisted in the cloud

### Table Definition

```sql
CREATE TABLE IF NOT EXISTS {user_name} (
    id UUID PRIMARY KEY,
    title VARCHAR,
    author VARCHAR,
    url VARCHAR,
    tags VARCHAR[],
    locations VARCHAR[],
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    markdown VARCHAR,
    properties JSON
);
```

The `properties` field stores the complete YAML frontmatter as JSON, allowing you to access all metadata from the original markdown file, even custom fields that are not part of the standard schema.