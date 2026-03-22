"use client";

import { useEffect } from "react";

interface ErrorPageProps {
  error: Error & { digest?: string };
  reset: () => void;
}

export default function GlobalError({ error, reset }: ErrorPageProps) {
  useEffect(() => {
    // TODO: send to error reporting service (e.g. Sentry)
    console.error("[MedPilot] Unhandled error:", error);
  }, [error]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-950 px-4 text-center">
      <div className="w-12 h-12 rounded-2xl bg-red-50 dark:bg-red-900/20 flex items-center justify-center mb-5">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor"
          strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className="text-red-500">
          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0zM12 9v4M12 17h.01" />
        </svg>
      </div>
      <h1 className="font-serif text-2xl font-medium text-gray-900 dark:text-gray-100 mb-2">
        Đã xảy ra lỗi
      </h1>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-6 max-w-xs">
        {error.message || "Lỗi không xác định. Vui lòng thử lại hoặc liên hệ hỗ trợ."}
      </p>
      <button
        onClick={reset}
        className="text-sm font-medium px-5 py-2 rounded-lg bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-800 transition-colors"
      >
        Thử lại
      </button>
    </div>
  );
}
