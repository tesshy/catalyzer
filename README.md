# Catalyzer: Catalog System for Datalake

Catalyzer is a comprehensive catalog system for datalakes, allowing users to organize and discover data assets efficiently.

## Components

### Catalyzer::Cabinet

A backend service for managing catalog entries using markdown files. The Cabinet component provides:

- CRUD operations for catalog markdown files
- Search functionality (tag-based and full-text search)
- DuckDB-based storage

[Learn more about Catalyzer::Cabinet](./cabinet/README.md)

## Getting Started

See the README in each component directory for specific installation and usage instructions.

## システム概要

Catalyzerは、Datalakeにアップロードされた各データファイルに対して、
その所在・メタデータ等をYAML front matter付きMarkdownで記述した「目録」を自動生成・管理するためのシステムです。

ここでのDatalakeとは、特定のデータストレージを指すのではなく、URLを持つ全てのデータををまとめたものを指します。
つまり、ネットワーク上に存在する全てのデータを対象として「目録」を生成・管理することを目的としています。

## 実現に必要な主な要素

- データファイルの検出・クロール機能
  - Datalake上の新規/更新データを検出し、目録生成対象を特定する
- 目録（カタログ）ファイルの自動生成
  - 各データごとにMarkdownファイルを作成
  - YAML front matterに以下のような情報を記載
    - データのパスやURL
    - ファイル名、サイズ、更新日時
    - データの説明やタグ
    - 所有者や管理者情報
- 目録の保存・管理
  - 生成したMarkdownファイルを一元管理する仕組み
  - バージョン管理や検索性の確保
- Web UI/API
  - 目録の閲覧・検索・編集を行うためのインターフェース
- メタデータの拡張性
  - 必要に応じてYAML front matterの項目を拡張可能にする

## Markdownファイルの例

```markdown
---
title: data1.csv
owner: user@example.com
author: tesshy@gmail.com
path: /datalake/path/to/data1.csv
created_at: 2025-01-01T12:34:56Z
updated_at: 2025-05-20T12:34:56Z
tags: [sample, csv]
---
# data1.csv

このデータは...
```