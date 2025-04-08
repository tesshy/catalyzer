# CKAN Schema Definition

This document outlines the database schema based on CKAN's data model, adapted for implementation with Cloudflare Worker and D1.

## Core Entities

CKAN's data model revolves around these primary entities:

- Organizations
- Datasets (Packages)
- Resources
- Groups
- Users
- Tags
- Activity

## Schema Details

### Users

```sql
CREATE TABLE "user" (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  email TEXT UNIQUE,
  password TEXT,
  fullname TEXT,
  created TIMESTAMP,
  about TEXT,
  sysadmin BOOLEAN DEFAULT FALSE,
  state TEXT DEFAULT 'active',
  image_url TEXT
);
```

### Organizations

```sql
CREATE TABLE organization (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  title TEXT,
  description TEXT,
  created TIMESTAMP,
  state TEXT DEFAULT 'active',
  type TEXT DEFAULT 'organization',
  is_organization BOOLEAN DEFAULT TRUE,
  image_url TEXT,
  approval_status TEXT DEFAULT 'approved'
);

CREATE TABLE member (
  id TEXT PRIMARY KEY,
  table_id TEXT,
  table_name TEXT,
  capacity TEXT,
  group_id TEXT,
  state TEXT DEFAULT 'active',
  FOREIGN KEY (group_id) REFERENCES organization(id)
);
```

### Datasets (Packages)

```sql
CREATE TABLE package (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  title TEXT,
  version TEXT,
  url TEXT,
  notes TEXT,
  license_id TEXT,
  author TEXT,
  author_email TEXT,
  maintainer TEXT,
  maintainer_email TEXT,
  created TIMESTAMP,
  state TEXT DEFAULT 'active',
  type TEXT DEFAULT 'dataset',
  owner_org TEXT,
  private BOOLEAN DEFAULT FALSE,
  metadata_created TIMESTAMP,
  metadata_modified TIMESTAMP,
  FOREIGN KEY (owner_org) REFERENCES organization(id)
);
```

### Resources

```sql
CREATE TABLE resource (
  id TEXT PRIMARY KEY,
  package_id TEXT NOT NULL,
  url TEXT,
  format TEXT,
  description TEXT,
  position INTEGER,
  created TIMESTAMP,
  last_modified TIMESTAMP,
  hash TEXT,
  size BIGINT,
  name TEXT,
  resource_type TEXT,
  mimetype TEXT,
  mimetype_inner TEXT,
  state TEXT DEFAULT 'active',
  FOREIGN KEY (package_id) REFERENCES package(id)
);
```

### Groups

```sql
CREATE TABLE "group" (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  title TEXT,
  description TEXT,
  created TIMESTAMP,
  state TEXT DEFAULT 'active',
  type TEXT DEFAULT 'group',
  is_organization BOOLEAN DEFAULT FALSE,
  image_url TEXT,
  approval_status TEXT DEFAULT 'approved'
);

CREATE TABLE package_group (
  id TEXT PRIMARY KEY,
  package_id TEXT,
  group_id TEXT,
  state TEXT DEFAULT 'active',
  FOREIGN KEY (package_id) REFERENCES package(id),
  FOREIGN KEY (group_id) REFERENCES "group"(id)
);
```

### Tags

```sql
CREATE TABLE tag (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL UNIQUE,
  vocabulary_id TEXT,
  state TEXT DEFAULT 'active'
);

CREATE TABLE package_tag (
  id TEXT PRIMARY KEY,
  package_id TEXT,
  tag_id TEXT,
  state TEXT DEFAULT 'active',
  FOREIGN KEY (package_id) REFERENCES package(id),
  FOREIGN KEY (tag_id) REFERENCES tag(id)
);
```

### Activity

```sql
CREATE TABLE activity (
  id TEXT PRIMARY KEY,
  timestamp TIMESTAMP,
  user_id TEXT,
  object_id TEXT,
  revision_id TEXT,
  activity_type TEXT,
  data TEXT, -- JSON data
  FOREIGN KEY (user_id) REFERENCES "user"(id)
);
```

### Extras (Custom Metadata)

```sql
CREATE TABLE package_extra (
  id TEXT PRIMARY KEY,
  package_id TEXT NOT NULL,
  key TEXT,
  value TEXT,
  state TEXT DEFAULT 'active',
  FOREIGN KEY (package_id) REFERENCES package(id)
);

CREATE TABLE resource_extra (
  id TEXT PRIMARY KEY,
  resource_id TEXT NOT NULL,
  key TEXT,
  value TEXT,
  state TEXT DEFAULT 'active',
  FOREIGN KEY (resource_id) REFERENCES resource(id)
);
```

## Relationships

1. **Organizations to Datasets**: One-to-many (an organization can have many datasets)
2. **Datasets to Resources**: One-to-many (a dataset can have many resources)
3. **Groups to Datasets**: Many-to-many (through package_group)
4. **Tags to Datasets**: Many-to-many (through package_tag)
5. **Users to Organizations**: Many-to-many (through member)

## Implementation Notes

1. UUID strings are recommended for ID fields
2. Timestamp fields should be stored in ISO format
3. State fields track deletion status (active/deleted)
4. Consider indexing commonly queried fields
5. The "data" field in activity table stores serialized JSON

For Cloudflare D1 implementation:
- D1 uses SQLite syntax
- Consider appropriate indexing for query performance
- Use prepared statements for all database operations
