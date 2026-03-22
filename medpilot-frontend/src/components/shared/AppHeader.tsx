"use client";

import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth.store";
import { clearSessionCookie } from "@/lib/utils/session";
import { Badge } from "@/components/ui";

interface AppHeaderProps {
  /** Override the displayed user/role info */
  subtitle?: string;
}

export function AppHeader({ subtitle }: AppHeaderProps) {
  const { user, logout } = useAuthStore();
  const router = useRouter();

  function handleLogout() {
    clearSessionCookie();
    logout();
    router.push("/auth/login");
  }

  return (
    <header className="sticky top-0 z-20 bg-white dark:bg-gray-950 border-b border-gray-100 dark:border-gray-800 h-14 flex items-center justify-between px-5">
      {/* Brand */}
      <div className="flex items-center gap-2.5">
        <BrainIcon />
        <span className="font-serif text-[17px] font-medium tracking-tight text-gray-900 dark:text-gray-100">
          MedPilot
        </span>
        {user && (
          <Badge variant={user.role === "doctor" ? "info" : "success"}>
            {user.role === "doctor" ? "Bác sĩ" : "Bệnh nhân"}
          </Badge>
        )}
      </div>

      {/* Right side */}
      <div className="flex items-center gap-4">
        {user && (
          <div className="text-right hidden sm:block">
            <p className="text-sm font-medium text-gray-800 dark:text-gray-200 leading-tight">
              {user.name}
            </p>
            <p className="text-xs text-gray-400 leading-tight">
              {subtitle ?? user.hospital ?? ""}
            </p>
          </div>
        )}
        <button
          onClick={handleLogout}
          className="flex items-center gap-1.5 text-xs text-gray-500 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
        >
          <LogoutIcon />
          Đăng xuất
        </button>
      </div>
    </header>
  );
}

function BrainIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"
      strokeLinecap="round" strokeLinejoin="round" className="text-blue-600">
      <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2" />
    </svg>
  );
}

function LogoutIcon() {
  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9" />
    </svg>
  );
}
