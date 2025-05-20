---
title: data1.csv
author: b@contoso.com
url: https://contoso.com/data1.md
tags: [sample, csv]
locations: ["https://contoso.com/data1.csv"]
created_at: 2025-01-01T12:34:56Z
updated_at: 2025-05-20T12:34:56Z   
---
# data1.csv

This dataset contains sample data for demonstration purposes.

## Schema

| Column | Type   | Description     |
|--------|--------|-----------------|
| id     | string | Primary key     |
| name   | string | Item name       |
| value  | number | Numerical value |
| date   | date   | Creation date   |

## Usage Examples

```python
import pandas as pd

# Load the data
df = pd.read_csv("https://contoso.com/data1.csv")

# Display first few rows
print(df.head())
```

## Notes

This data is updated monthly. Please check the `updated_at` field for the latest version.