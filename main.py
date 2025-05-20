"""
Catalyzer: Catalog System for Datalake
実装: Catalyzer::Cabinet API for storing and operating on Markdown catalog files
"""
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid
import duckdb
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# アプリケーション初期化
app = FastAPI(
    title="Catalyzer::Cabinet",
    description="API for storing and operating on Markdown catalog files",
    version="0.1.0"
)

# DuckDB接続設定
DB_PATH = os.environ.get("DUCKDB_PATH", ":memory:")
conn = duckdb.connect(DB_PATH)

# テーブルスキーマ定義と作成
conn.execute("""
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
""")

# データモデル定義
class CatalogBase(BaseModel):
    title: str
    author: str
    url: Optional[str] = None
    tags: List[str] = []
    locations: List[str] = []
    content: str

class CatalogCreate(CatalogBase):
    pass

class CatalogUpdate(CatalogBase):
    pass

class Catalog(CatalogBase):
    id: str
    created_at: datetime
    updated_at: datetime

# サンプルデータ挿入用の関数（テスト用）
def insert_sample_data():
    """サンプルデータをDBに挿入する関数"""
    sample_id = str(uuid.uuid4())
    current_time = datetime.now()
    
    conn.execute("""
        INSERT INTO cabinet 
        (id, title, author, url, tags, locations, created_at, updated_at, content)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        sample_id, 
        "サンプルカタログ", 
        "山田太郎", 
        "https://example.com", 
        ["サンプル", "テスト", "マークダウン"], 
        ["東京", "大阪"],
        current_time,
        current_time,
        "# サンプルカタログ\n\nこれはサンプルのマークダウンコンテンツです。"
    ))
    
    return sample_id

# APIエンドポイント実装
@app.post("/catalogs", response_model=Catalog, status_code=201)
def create_catalog(catalog: CatalogCreate):
    """カタログMarkdownファイルの登録 (Create)"""
    catalog_id = str(uuid.uuid4())
    current_time = datetime.now()
    
    try:
        conn.execute("""
            INSERT INTO cabinet 
            (id, title, author, url, tags, locations, created_at, updated_at, content)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            catalog_id, 
            catalog.title, 
            catalog.author, 
            catalog.url, 
            catalog.tags, 
            catalog.locations,
            current_time,
            current_time,
            catalog.content
        ))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"データベース操作エラー: {str(e)}")
    
    # 作成したカタログを返す
    result = conn.execute(f"SELECT * FROM cabinet WHERE id = '{catalog_id}'").fetchone()
    return {
        "id": str(result[0]),
        "title": result[1],
        "author": result[2],
        "url": result[3],
        "tags": result[4],
        "locations": result[5],
        "created_at": result[6],
        "updated_at": result[7],
        "content": result[8]
    }

@app.put("/catalogs/{catalog_id}", response_model=Catalog)
def update_catalog(catalog_id: str, catalog: CatalogUpdate):
    """カタログMarkdownファイルの更新 (Update)"""
    # カタログの存在確認
    result = conn.execute(f"SELECT id FROM cabinet WHERE id = '{catalog_id}'").fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="指定されたIDのカタログが見つかりません")
    
    current_time = datetime.now()
    
    try:
        conn.execute("""
            UPDATE cabinet 
            SET title = ?, author = ?, url = ?, tags = ?, locations = ?, 
            updated_at = ?, content = ?
            WHERE id = ?
        """, (
            catalog.title, 
            catalog.author, 
            catalog.url, 
            catalog.tags, 
            catalog.locations,
            current_time,
            catalog.content,
            catalog_id
        ))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"データベース操作エラー: {str(e)}")
    
    # 更新したカタログを返す
    result = conn.execute(f"SELECT * FROM cabinet WHERE id = '{catalog_id}'").fetchone()
    return {
        "id": str(result[0]),
        "title": result[1],
        "author": result[2],
        "url": result[3],
        "tags": result[4],
        "locations": result[5],
        "created_at": result[6],
        "updated_at": result[7],
        "content": result[8]
    }

@app.delete("/catalogs/{catalog_id}", status_code=204)
def delete_catalog(catalog_id: str):
    """カタログMarkdownファイルの削除 (Delete)"""
    # カタログの存在確認
    result = conn.execute(f"SELECT id FROM cabinet WHERE id = '{catalog_id}'").fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="指定されたIDのカタログが見つかりません")
    
    try:
        conn.execute(f"DELETE FROM cabinet WHERE id = '{catalog_id}'")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"データベース操作エラー: {str(e)}")
    
    return None

@app.get("/catalogs/search", response_model=List[Catalog])
def search_catalogs(tag: Optional[str] = None, q: Optional[str] = None):
    """目録の検索 (Search)"""
    if not tag and not q:
        raise HTTPException(status_code=400, detail="検索パラメータが指定されていません。'tag'または'q'を指定してください。")
    
    try:
        if tag:
            # タグ検索
            results = conn.execute(f"SELECT * FROM cabinet WHERE array_contains(tags, '{tag}')").fetchall()
        elif q:
            # フルテキスト検索（title、author、contentに対して）
            results = conn.execute(f"""
                SELECT * FROM cabinet 
                WHERE title LIKE '%{q}%' 
                OR author LIKE '%{q}%' 
                OR content LIKE '%{q}%'
            """).fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"検索処理エラー: {str(e)}")
    
    catalogs = []
    for r in results:
        catalogs.append({
            "id": str(r[0]),
            "title": r[1],
            "author": r[2],
            "url": r[3],
            "tags": r[4],
            "locations": r[5],
            "created_at": r[6],
            "updated_at": r[7],
            "content": r[8]
        })
    
    return catalogs

@app.get("/catalogs/{catalog_id}", response_model=Catalog)
def get_catalog(catalog_id: str):
    """カタログMarkdownファイルの取得 (Read)"""
    try:
        result = conn.execute(f"SELECT * FROM cabinet WHERE id = '{catalog_id}'").fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="指定されたIDのカタログが見つかりません")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"データベース操作エラー: {str(e)}")
    
    return {
        "id": str(result[0]),
        "title": result[1],
        "author": result[2],
        "url": result[3],
        "tags": result[4],
        "locations": result[5],
        "created_at": result[6],
        "updated_at": result[7],
        "content": result[8]
    }

@app.get("/catalogs", response_model=List[Catalog])
def list_catalogs():
    """すべてのカタログMarkdownファイルのリスト取得"""
    try:
        results = conn.execute("SELECT * FROM cabinet").fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"データベース操作エラー: {str(e)}")
    
    catalogs = []
    for r in results:
        catalogs.append({
            "id": str(r[0]),
            "title": r[1],
            "author": r[2],
            "url": r[3],
            "tags": r[4],
            "locations": r[5],
            "created_at": r[6],
            "updated_at": r[7],
            "content": r[8]
        })
    
    return catalogs

# サンプルデータ挿入用エンドポイント（デモンストレーション用）
@app.post("/sample", status_code=201)
def create_sample():
    """サンプルデータを作成するエンドポイント"""
    sample_id = insert_sample_data()
    return {"message": "サンプルデータが作成されました", "id": sample_id}

# アプリケーション起動コード（直接実行時のみ）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)