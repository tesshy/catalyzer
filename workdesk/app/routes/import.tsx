import { useState, useRef } from "react";
import type { Route } from "./+types/import";
import { WorkdeskLayout } from "../components/WorkdeskLayout";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "データインポート - Workdesk" },
    { name: "description", content: "CSVファイルをドラッグ&ドロップでDuckDBにインポート" },
  ];
}

export default function DataImport() {
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer.files).filter(
      file => file.type === 'text/csv' || file.name.endsWith('.csv')
    );
    
    if (files.length > 0) {
      setUploadedFiles(prev => [...prev, ...files]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setUploadedFiles(prev => [...prev, ...files]);
  };

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleImport = async () => {
    if (uploadedFiles.length === 0) return;
    
    setIsProcessing(true);
    
    // TODO: DuckDB WASM integration
    setTimeout(() => {
      setIsProcessing(false);
      alert(`${uploadedFiles.length}個のファイルがインポートされました`);
      setUploadedFiles([]);
    }, 2000);
  };

  return (
    <WorkdeskLayout>
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            データインポート
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            CSVファイルをDuckDBにインポートします
          </p>
        </div>

        {/* Upload area */}
        <div className="mb-8">
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              isDragOver
                ? 'border-blue-400 bg-blue-50 dark:bg-blue-900/20'
                : 'border-gray-300 dark:border-gray-600'
            }`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <div className="space-y-4">
              <div className="flex justify-center">
                <svg
                  className="h-12 w-12 text-gray-400"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
              </div>
              <div>
                <p className="text-lg text-gray-600 dark:text-gray-400">
                  CSVファイルをドラッグ&ドロップ
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-500">
                  または
                  <button
                    type="button"
                    className="mx-1 text-blue-600 hover:text-blue-500"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    ファイルを選択
                  </button>
                  してください
                </p>
              </div>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept=".csv"
              className="hidden"
              onChange={handleFileInput}
            />
          </div>
        </div>

        {/* Uploaded files list */}
        {uploadedFiles.length > 0 && (
          <div className="mb-8">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
              アップロード済みファイル
            </h3>
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
              <ul className="divide-y divide-gray-200 dark:divide-gray-700">
                {uploadedFiles.map((file, index) => (
                  <li key={index} className="px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center">
                      <svg
                        className="h-8 w-8 text-gray-400 mr-3"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                        />
                      </svg>
                      <div>
                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                          {file.name}
                        </p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {(file.size / 1024).toFixed(1)} KB
                        </p>
                      </div>
                    </div>
                    <button
                      type="button"
                      className="text-red-600 hover:text-red-500"
                      onClick={() => removeFile(index)}
                    >
                      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                        />
                      </svg>
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {/* Import button */}
        {uploadedFiles.length > 0 && (
          <div className="flex justify-end">
            <button
              type="button"
              disabled={isProcessing}
              onClick={handleImport}
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isProcessing ? (
                <>
                  <svg
                    className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
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
                  インポート中...
                </>
              ) : (
                `${uploadedFiles.length}個のファイルをインポート`
              )}
            </button>
          </div>
        )}
      </div>
    </WorkdeskLayout>
  );
}