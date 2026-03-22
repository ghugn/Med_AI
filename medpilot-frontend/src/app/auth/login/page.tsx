"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth.store";
import { setSessionCookie } from "@/lib/utils/session";
import type { User, UserRole } from "@/types";

const MOCK_USERS: Record<UserRole, User> = {
  doctor: {
    id: "doc_001",
    name: "BS. Nguyễn Thành Long",
    role: "doctor",
    department: "Da liễu",
    hospital: "BV Bạch Mai",
  },
  patient: {
    id: "pat_001",
    name: "Trần Thị Bình",
    role: "patient",
  },
};

export default function LoginPage() {
  const router = useRouter();
  const login = useAuthStore((s) => s.login);
  const [loading, setLoading] = useState<UserRole | null>(null);

  async function handleLogin(role: UserRole) {
    setLoading(role);
    // Simulate auth handshake — replace with real API call
    await new Promise((r) => setTimeout(r, 700));
    const user = MOCK_USERS[role];
    login(user);
    // Set cookie so middleware can read role on the Edge
    setSessionCookie({ role: user.role, userId: user.id, name: user.name });
    router.push(role === "doctor" ? "/doctor/scribe" : "/patient/chat");
  }

  return (
    <main className="min-h-screen bg-gray-50 dark:bg-gray-950 flex flex-col items-center justify-center px-4">
      {/* Hero */}
      <div className="text-center mb-10">
        <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-blue-50 dark:bg-blue-900/30 mb-4">
          <BrainIcon />
        </div>
        <h1 className="font-serif text-3xl font-medium text-gray-900 dark:text-gray-100 mb-2">
          MedPilot
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Hệ thống hỗ trợ Da liễu thông minh
        </p>
      </div>

      {/* Role cards */}
      <div className="w-full max-w-sm flex flex-col gap-3">
        <RoleCard
          role="doctor"
          title="Bác sĩ"
          description="Medical Scribe · Clinical Reminder"
          icon={<StethoscopeIcon />}
          loading={loading === "doctor"}
          disabled={!!loading}
          onClick={() => handleLogin("doctor")}
        />
        <RoleCard
          role="patient"
          title="Bệnh nhân"
          description="Hỏi đáp Da liễu AI"
          icon={<UserIcon />}
          loading={loading === "patient"}
          disabled={!!loading}
          onClick={() => handleLogin("patient")}
        />

        <p className="text-center text-xs text-gray-400 mt-2">
          Demo — dữ liệu mẫu, không kết nối hệ thống thật
        </p>
      </div>
    </main>
  );
}

interface RoleCardProps {
  role: UserRole;
  title: string;
  description: string;
  icon: React.ReactNode;
  loading: boolean;
  disabled: boolean;
  onClick: () => void;
}

function RoleCard({ title, description, icon, loading, disabled, onClick }: RoleCardProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="w-full flex items-center gap-4 bg-white dark:bg-gray-900 border border-gray-100 dark:border-gray-800 rounded-2xl p-5 text-left hover:border-blue-200 dark:hover:border-blue-800 hover:shadow-sm transition-all disabled:opacity-60 disabled:cursor-wait group"
    >
      <div className="w-11 h-11 rounded-xl bg-blue-50 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400 shrink-0 group-hover:bg-blue-100 dark:group-hover:bg-blue-900/50 transition-colors">
        {loading ? <SpinnerIcon /> : icon}
      </div>
      <div>
        <p className="font-medium text-gray-900 dark:text-gray-100">{title}</p>
        <p className="text-xs text-gray-400 mt-0.5">{description}</p>
      </div>
      <ArrowIcon className="ml-auto text-gray-300 dark:text-gray-600 group-hover:text-blue-400 transition-colors" />
    </button>
  );
}

// ─── Icons ────────────────────────────────────────────────────────────────────

function BrainIcon() {
  return (
    <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6"
      strokeLinecap="round" strokeLinejoin="round" className="text-blue-600 dark:text-blue-400">
      <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2" />
    </svg>
  );
}

function StethoscopeIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"
      strokeLinecap="round" strokeLinejoin="round">
      <path d="M4.8 2.3A.3.3 0 1 0 5 2H4a2 2 0 0 0-2 2v5a6 6 0 0 0 6 6v0a6 6 0 0 0 6-6V4a2 2 0 0 0-2-2h-1a.3.3 0 1 0 .2.3" />
      <path d="M8 15a6 6 0 0 0 6 6 6 6 0 0 0 6-6v-3" />
      <circle cx="20" cy="10" r="2" />
    </svg>
  );
}

function UserIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"
      strokeLinecap="round" strokeLinejoin="round">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8z" />
    </svg>
  );
}

function ArrowIcon({ className }: { className?: string }) {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
      strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M9 18l6-6-6-6" />
    </svg>
  );
}

function SpinnerIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
      strokeLinecap="round" strokeLinejoin="round" className="animate-spin">
      <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" />
    </svg>
  );
}
