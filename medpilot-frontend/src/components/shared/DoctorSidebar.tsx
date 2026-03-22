"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils/cn";
import { SectionLabel } from "@/components/ui";

const NAV_ITEMS = [
  { href: "/doctor/scribe",   label: "Medical Scribe",    icon: MicIcon },
  { href: "/doctor/reminder", label: "Clinical Reminder", icon: BellIcon },
];

const MOCK_PATIENTS = [
  { id: "P001", name: "Nguyễn Văn An",   age: 28 },
  { id: "P002", name: "Trần Thị Bình",   age: 34 },
  { id: "P003", name: "Lê Minh Cường",   age: 45 },
];

export function DoctorSidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-52 shrink-0 bg-white dark:bg-gray-950 border-r border-gray-100 dark:border-gray-800 flex flex-col p-3 gap-1">
      {NAV_ITEMS.map(({ href, label, icon: Icon }) => (
        <Link
          key={href}
          href={href}
          className={cn(
            "flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors",
            pathname === href
              ? "bg-blue-50 text-blue-700 font-medium dark:bg-blue-900/30 dark:text-blue-400"
              : "text-gray-500 hover:bg-gray-50 dark:text-gray-400 dark:hover:bg-gray-800"
          )}
        >
          <Icon />
          {label}
        </Link>
      ))}

      {/* Today's patients */}
      <div className="mt-auto pt-4 border-t border-gray-100 dark:border-gray-800">
        <SectionLabel>Hôm nay</SectionLabel>
        {MOCK_PATIENTS.map((p) => (
          <div key={p.id} className="px-3 py-2 rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
            <p className="text-sm font-medium text-gray-800 dark:text-gray-200 leading-tight">{p.name}</p>
            <p className="text-xs text-gray-400 leading-none mt-0.5">{p.age} tuổi</p>
          </div>
        ))}
      </div>
    </aside>
  );
}

function MicIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3zM19 10v2a7 7 0 0 1-14 0v-2M12 19v4M8 23h8" />
    </svg>
  );
}

function BellIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 0 1-3.46 0" />
    </svg>
  );
}
