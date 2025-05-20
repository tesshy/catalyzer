# Catalyzer::Cabinet: Cabinet system for Markdown


## 概要
Catalyzer::Cabinetは、Markdownで記述された（目録Markdownファイル）を保存するためのシステムです。
Markdownはプレインテキストファイルで保持・運用されることをが多いですが、目録として機能させるためには横断的に探索を行う必要があります。
そのため、本システムではDuckDBにMarkdown目録ファイルを記録し、その配下で包括的なオペレーションを行うことを目的とします。


## 実装
Catalyzer::Cabinetは以下のコンポーネントを使用して実装されます。直近フロントエンドをは提供されません。

- Python 3.12
- FastAPI
- DuckDB or MotherDuck

## 機能

- 目録Markdownファイル
    - 登録
    - 更新
    - 削除
- 目録の検索
    - タグ検索
    - フルテキスト検索

### 目録Markdownファイル仕様

```markdown
---
title: data1.csv # タイトル
author: b@contoso.com # 著者のメールアドレス
url: https://contoso.com/data1.md # 目録Markdownファイルの場所
tags: [sample, csv] # タグ
locations: ["https://contoso.com/data1.csv" ] # 目録が表す情報の場所、複数個指定可能
created_at: 2025-01-01T12:34:56Z # 目録作成日時
updated_at: 2025-05-20T12:34:56Z # 目録更新日時   
---
# data1.csv

このデータは...
```

### DuckDB構造

- Database: Groupに対応します。例えばA部署のデータであれば、”A”というデータベース名になります。
- Table: Userに対応します。例えばBさんのデータであれば、"B"というテーブル名になります。想定されるケースは内部で使用されるユーザー識別子です（e.g. UUID）
- Record: 1つのMarkdownファイルに対応します。

#### テーブル定義

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

```sql
-- テスト用サンプルデータの挿入
INSERT INTO cabinet (
    id, title, author, url, tags, locations, created_at, updated_at, content
) VALUES (
    '123e4567-e89b-12d3-a456-426614174000',
    'data1.csv',
    'b@contoso.com',
    'https://contoso.com/data1.md',
    ['sample', 'csv'],
    ['https://contoso.com/data1.csv'],
    '2025-01-01T12:34:56Z',
    '2025-05-20T12:34:56Z',
    '# data1.csv\n\nこのデータは...'
);
```

## 参考資料

- https://www.loc.gov/marc/bibliographic/bd856.html
