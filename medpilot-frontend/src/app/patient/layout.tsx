import { AppHeader } from "@/components/shared/AppHeader";

export default function PatientLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="h-screen flex flex-col bg-gray-50 dark:bg-gray-950 overflow-hidden">
      <AppHeader subtitle="Hỏi đáp Da liễu" />
      <div className="flex-1 flex flex-col overflow-hidden max-w-3xl w-full mx-auto">
        {children}
      </div>
    </div>
  );
}
