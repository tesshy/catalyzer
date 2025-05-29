import { useState } from "react";
import type { Route } from "./+types/catalog";
import { WorkdeskLayout } from "../components/WorkdeskLayout";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "データカタログ - Workdesk" },
    { name: "description", content: "テーブル構造とメタデータの管理" },
  ];
}

interface TableInfo {
  schema: string;
  name: string;
  type: string;
  rowCount: number;
  size: string;
  columns: ColumnInfo[];
}

interface ColumnInfo {
  name: string;
  type: string;
  nullable: boolean;
  defaultValue?: string;
}

export default function CatalogBrowser() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTable, setSelectedTable] = useState<TableInfo | null>(null);
  const [selectedSchema, setSelectedSchema] = useState("all");

  // Mock data - これは将来的にCatalyzr::CabinetのAPIと統合されます
  const mockTables: TableInfo[] = [
    {
      schema: "main",
      name: "sales_data",
      type: "BASE TABLE",
      rowCount: 1250000,
      size: "24.3 MB",
      columns: [
        { name: "id", type: "INTEGER", nullable: false },
        { name: "product_id", type: "VARCHAR", nullable: false },
        { name: "customer_id", type: "VARCHAR", nullable: false },
        { name: "sale_date", type: "DATE", nullable: false },
        { name: "amount", type: "DECIMAL(10,2)", nullable: false },
        { name: "quantity", type: "INTEGER", nullable: false },
        { name: "discount", type: "DECIMAL(5,2)", nullable: true },
      ]
    },
    {
      schema: "main",
      name: "customers",
      type: "BASE TABLE",
      rowCount: 45000,
      size: "8.7 MB",
      columns: [
        { name: "customer_id", type: "VARCHAR", nullable: false },
        { name: "first_name", type: "VARCHAR", nullable: false },
        { name: "last_name", type: "VARCHAR", nullable: false },
        { name: "email", type: "VARCHAR", nullable: true },
        { name: "phone", type: "VARCHAR", nullable: true },
        { name: "created_at", type: "TIMESTAMP", nullable: false },
      ]
    },
    {
      schema: "analytics",
      name: "monthly_summary",
      type: "VIEW",
      rowCount: 24,
      size: "1.2 KB",
      columns: [
        { name: "month", type: "DATE", nullable: false },
        { name: "total_sales", type: "DECIMAL(15,2)", nullable: false },
        { name: "customer_count", type: "INTEGER", nullable: false },
        { name: "avg_order_value", type: "DECIMAL(10,2)", nullable: false },
      ]
    },
  ];

  const schemas = [...new Set(mockTables.map(t => t.schema))];
  
  const filteredTables = mockTables.filter(table => {
    const matchesSearch = table.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         table.schema.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSchema = selectedSchema === "all" || table.schema === selectedSchema;
    return matchesSearch && matchesSchema;
  });

  return (
    <WorkdeskLayout>
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            データカタログ
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            テーブル構造とメタデータの参照
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Tables List */}
          <div className="lg:col-span-2">
            {/* Filters */}
            <div className="mb-6 flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <input
                  type="text"
                  placeholder="テーブル名やスキーマで検索..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <select
                  value={selectedSchema}
                  onChange={(e) => setSelectedSchema(e.target.value)}
                  className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="all">全スキーマ</option>
                  {schemas.map(schema => (
                    <option key={schema} value={schema}>{schema}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Tables Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {filteredTables.map((table, index) => (
                <div
                  key={index}
                  className={`bg-white dark:bg-gray-800 shadow rounded-lg p-6 cursor-pointer transition-colors ${
                    selectedTable?.name === table.name
                      ? 'ring-2 ring-blue-500 bg-blue-50 dark:bg-blue-900/20'
                      : 'hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`}
                  onClick={() => setSelectedTable(table)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="text-lg font-medium text-gray-900 dark:text-white truncate">
                          {table.name}
                        </h3>
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          table.type === 'VIEW' 
                            ? 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100'
                            : 'bg-blue-100 text-blue-800 dark:bg-blue-800 dark:text-blue-100'
                        }`}>
                          {table.type}
                        </span>
                      </div>
                      <p className="text-sm text-gray-500 dark:text-gray-400 mb-3">
                        スキーマ: {table.schema}
                      </p>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">行数:</span>
                          <span className="ml-2 text-gray-900 dark:text-white">
                            {table.rowCount.toLocaleString()}
                          </span>
                        </div>
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">サイズ:</span>
                          <span className="ml-2 text-gray-900 dark:text-white">
                            {table.size}
                          </span>
                        </div>
                        <div className="col-span-2">
                          <span className="text-gray-500 dark:text-gray-400">カラム数:</span>
                          <span className="ml-2 text-gray-900 dark:text-white">
                            {table.columns.length}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {filteredTables.length === 0 && (
              <div className="text-center py-12">
                <div className="text-gray-400 mb-4">
                  <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  テーブルが見つかりません
                </h3>
                <p className="text-gray-500 dark:text-gray-400">
                  検索条件を変更してお試しください
                </p>
              </div>
            )}
          </div>

          {/* Table Details */}
          <div className="lg:col-span-1">
            {selectedTable ? (
              <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
                <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                    {selectedTable.name}
                  </h3>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {selectedTable.schema}.{selectedTable.name}
                  </p>
                </div>
                <div className="p-6">
                  <h4 className="text-md font-medium text-gray-900 dark:text-white mb-4">
                    カラム情報
                  </h4>
                  <div className="space-y-3">
                    {selectedTable.columns.map((column, index) => (
                      <div key={index} className="border border-gray-200 dark:border-gray-600 rounded-md p-3">
                        <div className="flex items-center justify-between mb-1">
                          <span className="font-medium text-gray-900 dark:text-white">
                            {column.name}
                          </span>
                          {!column.nullable && (
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100">
                              NOT NULL
                            </span>
                          )}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                          型: {column.type}
                        </div>
                        {column.defaultValue && (
                          <div className="text-sm text-gray-500 dark:text-gray-400">
                            デフォルト値: {column.defaultValue}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
                <div className="text-center text-gray-500 dark:text-gray-400">
                  <div className="mb-4">
                    <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                  </div>
                  <p>
                    テーブルを選択すると<br />
                    詳細情報が表示されます
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </WorkdeskLayout>
  );
}