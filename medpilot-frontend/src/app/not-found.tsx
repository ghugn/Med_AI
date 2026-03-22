import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-950 px-4 text-center">
      <p className="text-7xl font-serif font-medium text-gray-200 dark:text-gray-800 mb-4 select-none">
        404
      </p>
      <h1 className="font-serif text-2xl font-medium text-gray-900 dark:text-gray-100 mb-2">
        Không tìm thấy trang
      </h1>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">
        Trang bạn tìm kiếm không tồn tại hoặc đã bị di chuyển.
      </p>
      <Link
        href="/auth/login"
        className="text-sm font-medium px-5 py-2 rounded-lg bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-800 transition-colors"
      >
        Về trang đăng nhập
      </Link>
    </div>
  );
}
