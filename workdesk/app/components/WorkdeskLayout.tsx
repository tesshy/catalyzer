import { Link, useLocation } from "react-router";

interface WorkdeskLayoutProps {
  children: React.ReactNode;
}

export function WorkdeskLayout({ children }: WorkdeskLayoutProps) {
  const location = useLocation();

  const navigation = [
    { name: 'ダッシュボード', href: '/', current: location.pathname === '/' },
    { name: 'データインポート', href: '/import', current: location.pathname === '/import' },
    { name: 'SQLクエリ', href: '/query', current: location.pathname === '/query' },
    { name: 'データカタログ', href: '/catalog', current: location.pathname === '/catalog' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Link to="/">
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                    Workdesk
                  </h1>
                </Link>
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  DuckLake管理ツール
                </p>
              </div>
            </div>
            <nav className="hidden md:flex space-x-8">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    item.current
                      ? 'text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900'
                      : 'text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white'
                  }`}
                >
                  {item.name}
                </Link>
              ))}
            </nav>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {children}
        </div>
      </main>
    </div>
  );
}