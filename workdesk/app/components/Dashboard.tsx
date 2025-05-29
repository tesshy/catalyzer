import { Link } from "react-router";
import { WorkdeskLayout } from "./WorkdeskLayout";

export function Dashboard() {
  return (
    <WorkdeskLayout>
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
          ダッシュボード
        </h2>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          DuckDBを使用したDataLakeの管理と分析
        </p>
      </div>

      {/* Quick stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        {stats.map((stat) => (
          <div
            key={stat.name}
            className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg"
          >
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <stat.icon
                    className="h-6 w-6 text-gray-400"
                    aria-hidden="true"
                  />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400 truncate">
                      {stat.name}
                    </dt>
                    <dd className="text-lg font-medium text-gray-900 dark:text-white">
                      {stat.value}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Action cards */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {actions.map((action) => (
          <div
            key={action.title}
            className="bg-white dark:bg-gray-800 shadow rounded-lg p-6"
          >
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <action.icon
                  className="h-8 w-8 text-blue-500"
                  aria-hidden="true"
                />
              </div>
              <div className="ml-5 w-0 flex-1">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                  {action.title}
                </h3>
                <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                  {action.description}
                </p>
              </div>
            </div>
            <div className="mt-4">
              <Link
                to={action.href}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                {action.buttonText}
              </Link>
            </div>
          </div>
        ))}
      </div>
    </WorkdeskLayout>
  );
}

const stats = [
  {
    name: 'データベース',
    value: '3',
    icon: (props: any) => (
      <svg {...props} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
      </svg>
    ),
  },
  {
    name: 'テーブル',
    value: '24',
    icon: (props: any) => (
      <svg {...props} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M3 14h18m-9-4v8m-7 0V4a1 1 0 011-1h16a1 1 0 011 1v16a1 1 0 01-1 1H5a1 1 0 01-1-1z" />
      </svg>
    ),
  },
  {
    name: 'レコード数',
    value: '1.2M',
    icon: (props: any) => (
      <svg {...props} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
  },
  {
    name: 'ストレージ',
    value: '42.3GB',
    icon: (props: any) => (
      <svg {...props} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8a7 7 0 1114 0v0a7 7 0 11-14 0v0z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 2v20M2 12h20" />
      </svg>
    ),
  },
];

const actions = [
  {
    title: 'データをインポート',
    description: 'CSVファイルをドラッグ&ドロップでアップロードし、DuckDBに取り込みます',
    buttonText: 'インポート開始',
    href: '/import',
    icon: (props: any) => (
      <svg {...props} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
      </svg>
    ),
  },
  {
    title: 'SQLクエリ実行',
    description: 'インタラクティブなSQLエディタでデータを分析・操作できます',
    buttonText: 'クエリエディタ',
    href: '/query',
    icon: (props: any) => (
      <svg {...props} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    ),
  },
  {
    title: 'データカタログ',
    description: 'テーブル構造やスキーマ情報を一覧表示し、メタデータを管理できます',
    buttonText: 'カタログを見る',
    href: '/catalog',
    icon: (props: any) => (
      <svg {...props} fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
      </svg>
    ),
  },
];