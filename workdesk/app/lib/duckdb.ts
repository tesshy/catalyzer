import * as duckdb from '@duckdb/duckdb-wasm';

export class DuckDBService {
  private db: duckdb.AsyncDuckDB | null = null;
  private conn: duckdb.AsyncDuckDBConnection | null = null;

  async initialize(): Promise<void> {
    if (this.db) return;

    try {
      // DuckDB WASMの初期化
      const JSDELIVR_BUNDLES = duckdb.getJsDelivrBundles();
      const bundle = await duckdb.selectBundle(JSDELIVR_BUNDLES);
      const worker = await duckdb.createWorker(bundle.mainWorker!);
      const logger = new duckdb.ConsoleLogger();
      this.db = new duckdb.AsyncDuckDB(logger, worker);
      await this.db.instantiate(bundle.mainModule, bundle.pthreadWorker);
      
      // データベース接続の作成
      this.conn = await this.db.connect();
      
      console.log('DuckDB initialized successfully');
    } catch (error) {
      console.error('Failed to initialize DuckDB:', error);
      throw error;
    }
  }

  async executeQuery(query: string): Promise<any> {
    if (!this.conn) {
      throw new Error('Database not initialized');
    }

    try {
      const result = await this.conn.query(query);
      return {
        columns: result.schema.fields.map(field => field.name),
        rows: result.toArray().map(row => Object.values(row)),
        rowCount: result.numRows
      };
    } catch (error) {
      console.error('Query execution failed:', error);
      throw error;
    }
  }

  async loadCSV(file: File, tableName: string): Promise<void> {
    if (!this.conn) {
      throw new Error('Database not initialized');
    }

    try {
      // ファイルをバイナリとして読み込み
      const arrayBuffer = await file.arrayBuffer();
      const uint8Array = new Uint8Array(arrayBuffer);
      
      // DuckDBにファイルを登録
      await this.db!.registerFileBuffer(file.name, uint8Array);
      
      // テーブルとしてCSVを読み込み
      const createTableQuery = `
        CREATE TABLE ${tableName} AS 
        SELECT * FROM read_csv_auto('${file.name}')
      `;
      
      await this.conn.query(createTableQuery);
      console.log(`Table ${tableName} created from ${file.name}`);
    } catch (error) {
      console.error('CSV loading failed:', error);
      throw error;
    }
  }

  async getTables(): Promise<any[]> {
    if (!this.conn) {
      throw new Error('Database not initialized');
    }

    try {
      const result = await this.conn.query(`
        SELECT 
          table_schema, 
          table_name, 
          table_type 
        FROM information_schema.tables 
        WHERE table_schema NOT IN ('information_schema')
        ORDER BY table_schema, table_name
      `);
      
      return result.toArray();
    } catch (error) {
      console.error('Failed to get tables:', error);
      throw error;
    }
  }

  async getTableSchema(tableName: string): Promise<any[]> {
    if (!this.conn) {
      throw new Error('Database not initialized');
    }

    try {
      const result = await this.conn.query(`DESCRIBE ${tableName}`);
      return result.toArray();
    } catch (error) {
      console.error('Failed to get table schema:', error);
      throw error;
    }
  }

  async close(): Promise<void> {
    if (this.conn) {
      await this.conn.close();
      this.conn = null;
    }
    if (this.db) {
      await this.db.terminate();
      this.db = null;
    }
  }
}

// シングルトンインスタンス
export const duckDBService = new DuckDBService();