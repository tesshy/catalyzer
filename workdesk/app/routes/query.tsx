import { useState } from "react";
import type { Route } from "./+types/query";
import { WorkdeskLayout } from "../components/WorkdeskLayout";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "SQLクエリ - Workdesk" },
    { name: "description", content: "インタラクティブなSQLエディタでデータを分析" },
  ];
}

interface QueryResult {
  columns: string[];
  rows: any[][];
  executionTime: number;
}

export default function QueryInterface() {
  const [query, setQuery] = useState("SELECT * FROM information_schema.tables LIMIT 10;");
  const [isExecuting, setIsExecuting] = useState(false);
  const [results, setResults] = useState<QueryResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const executeQuery = async () => {
    if (!query.trim()) return;
    
    setIsExecuting(true);
    setError(null);
    
    try {
      // TODO: DuckDB WASM integration
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock result for demonstration
      const mockResult: QueryResult = {
        columns: ['table_schema', 'table_name', 'table_type'],
        rows: [
          ['main', 'sample_data', 'BASE TABLE'],
          ['information_schema', 'tables', 'VIEW'],
          ['information_schema', 'columns', 'VIEW'],
        ],
        executionTime: 45
      };
      
      setResults(mockResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'クエリの実行中にエラーが発生しました');
    } finally {
      setIsExecuting(false);
    }
  };

  const sampleQueries = [
    {
      name: "テーブル一覧",
      query: "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main';"
    },
    {
      name: "データ型確認",
      query: "DESCRIBE sample_data;"
    },
    {
      name: "データ集計",
      query: "SELECT COUNT(*) as row_count FROM sample_data;"
    },
    {
      name: "上位10件",
      query: "SELECT * FROM sample_data LIMIT 10;"
    }
  ];

  return (
    <WorkdeskLayout>
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            SQLクエリエディタ
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            DuckDBでインタラクティブにデータを分析
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Query Editor */}
          <div className="lg:col-span-3 space-y-6">
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
              <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  SQLエディタ
                </h3>
              </div>
              <div className="p-6">
                <textarea
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="w-full h-40 p-4 border border-gray-300 dark:border-gray-600 rounded-md bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white font-mono text-sm resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="SQLクエリを入力してください..."
                />
                <div className="mt-4 flex justify-between items-center">
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    Ctrl+Enter で実行
                  </div>
                  <button
                    type="button"
                    disabled={isExecuting || !query.trim()}
                    onClick={executeQuery}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isExecuting ? (
                      <>
                        <svg
                          className="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                          xmlns="http://www.w3.org/2000/svg"
                          fill="none"
                          viewBox="0 0 24 24"
                        >
                          <circle
                            className="opacity-25"
                            cx="12"
                            cy="12"
                            r="10"
                            stroke="currentColor"
                            strokeWidth="4"
                          ></circle>
                          <path
                            className="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                          ></path>
                        </svg>
                        実行中...
                      </>
                    ) : (
                      '実行'
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Results */}
            {error && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg
                      className="h-5 w-5 text-red-400"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
                      エラー
                    </h3>
                    <p className="mt-1 text-sm text-red-700 dark:text-red-300">
                      {error}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {results && (
              <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
                <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                  <div className="flex justify-between items-center">
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                      実行結果
                    </h3>
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      実行時間: {results.executionTime}ms | {results.rows.length}行
                    </span>
                  </div>
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                    <thead className="bg-gray-50 dark:bg-gray-700">
                      <tr>
                        {results.columns.map((column, index) => (
                          <th
                            key={index}
                            className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
                          >
                            {column}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                      {results.rows.map((row, rowIndex) => (
                        <tr key={rowIndex}>
                          {row.map((cell, cellIndex) => (
                            <td
                              key={cellIndex}
                              className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100"
                            >
                              {cell}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>

          {/* Sample Queries Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
              <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  サンプルクエリ
                </h3>
              </div>
              <div className="p-6">
                <div className="space-y-3">
                  {sampleQueries.map((sample, index) => (
                    <button
                      key={index}
                      type="button"
                      onClick={() => setQuery(sample.query)}
                      className="w-full text-left p-3 text-sm border border-gray-200 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <div className="font-medium text-gray-900 dark:text-white">
                        {sample.name}
                      </div>
                      <div className="mt-1 text-gray-500 dark:text-gray-400 font-mono text-xs truncate">
                        {sample.query}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </WorkdeskLayout>
  );
}