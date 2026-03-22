export default function ReminderLoading() {
  return (
    <div className="flex flex-col gap-5 animate-pulse">
      <div className="bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-xl p-5">
        <div className="h-5 w-48 bg-gray-100 dark:bg-gray-800 rounded mb-2" />
        <div className="h-3 w-72 bg-gray-100 dark:bg-gray-800 rounded mb-5" />
        <div className="h-16 w-full bg-gray-100 dark:bg-gray-800 rounded-lg mb-4" />
        <div className="h-9 w-36 bg-gray-100 dark:bg-gray-800 rounded-lg" />
      </div>
    </div>
  );
}
