import { AppHeader } from "@/components/shared/AppHeader";
import { DoctorSidebar } from "@/components/shared/DoctorSidebar";

export default function DoctorLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-950">
      <AppHeader />
      <div className="flex flex-1 overflow-hidden">
        <DoctorSidebar />
        <main className="flex-1 overflow-y-auto p-5">
          <div className="max-w-3xl mx-auto">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
