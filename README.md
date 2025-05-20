# Catalyzer: Catalog System for Datalake

Catalyzer は、マークダウン形式のカタログファイルを管理するためのシステムです。FastAPIとDuckDBを使用して、カタログの登録、更新、削除、検索などの操作を行うことができます。

## 機能

- カタログMarkdownファイルの登録 (Create)
- カタログMarkdownファイルの取得 (Read)
- カタログMarkdownファイルの更新 (Update)
- カタログMarkdownファイルの削除 (Delete)
- タグ検索
- フルテキスト検索

## インストール

```bash
pip install -r requirements.txt
```

## 使い方

### サーバーの起動

```bash
uvicorn main:app --reload
```

### APIドキュメント

サーバー起動後、以下のURLでSwagger UIにアクセスできます：

- http://localhost:8000/docs
- http://localhost:8000/redoc

## API仕様

### カタログの登録

```
POST /catalogs
```

リクエスト例:

```json
{
  "title": "サンプルカタログ",
  "author": "山田太郎",
  "url": "https://example.com",
  "tags": ["サンプル", "テスト"],
  "locations": ["東京", "大阪"],
  "content": "# サンプルカタログ\n\nこれはサンプルです。"
}
```

### カタログの更新

```
PUT /catalogs/{id}
```

### カタログの削除

```
DELETE /catalogs/{id}
```

### カタログの検索

タグ検索:
```
GET /catalogs/search?tag=サンプル
```

フルテキスト検索:
```
GET /catalogs/search?q=サンプル
```

## データベーススキーマ

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

