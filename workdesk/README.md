# Workdesk - DuckLake管理ツール

DuckDBを使用したDataLake管理のためのモダンなWebアプリケーション。React Router v7とTailwind CSSで構築されています。

## 機能

- 🦆 **DuckDB WASM統合** - ブラウザ内でのSQL実行
- 📊 **ダッシュボード** - データベースの概要と統計情報
- 📁 **データインポート** - CSVファイルのドラッグ&ドロップアップロード
- 🔍 **SQLクエリエディタ** - インタラクティブなSQL実行環境
- 📚 **データカタログ** - テーブル構造とメタデータの管理
- 🎨 **モダンUI** - Tailwind CSSによるプロフェッショナルなデザイン
- 🔒 **TypeScript** - 型安全な開発環境
- ⚡️ **React Router v7** - 最新のルーティングとデータローディング

## 技術スタック

- **Frontend**: React Router v7, TypeScript, Tailwind CSS
- **Database**: DuckDB WASM
- **Build Tool**: Vite
- **パッケージマネージャー**: npm

## セットアップ

### 依存関係のインストール

```bash
npm install
```

### 開発サーバーの起動

```bash
npm run dev
```

アプリケーションは `http://localhost:5173` で利用できます。

## 開発

### TypeScriptの型チェック

```bash
npm run typecheck
```

### 本番ビルド

```bash
npm run build
```

## アプリケーション構造

- `/` - ダッシュボード（概要と統計情報）
- `/import` - CSVファイルのインポート
- `/query` - SQLクエリエディタ
- `/catalog` - データカタログとテーブル構造

## DuckDBの使用方法

### CSVデータのインポート

1. `/import` ページを開く
2. CSVファイルをドラッグ&ドロップまたはファイル選択
3. 「インポート」ボタンをクリック

### SQLクエリの実行

1. `/query` ページを開く
2. SQLエディタにクエリを入力
3. 「実行」ボタンをクリックまたはCtrl+Enter

### テーブル構造の確認

1. `/catalog` ページを開く
2. テーブル一覧から対象テーブルを選択
3. カラム情報とメタデータを確認

## 今後の拡張予定

- [ ] Catalyzer::Cabinet APIとの統合
- [ ] データエクスポート機能
- [ ] 高度なクエリビルダー
- [ ] データ可視化機能
- [ ] ユーザー認証とアクセス制御

## デプロイメント

### Docker

```bash
docker build -t workdesk .
docker run -p 3000:3000 workdesk
```

### その他のプラットフォーム

`npm run build` の出力をサポートされているNode.jsホスティングプラットフォームにデプロイしてください：

- AWS ECS
- Google Cloud Run
- Azure Container Apps
- Vercel
- Netlify
- Railway

---

Built with ❤️ for DuckLake management using React Router v7.
