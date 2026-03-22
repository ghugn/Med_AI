import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MedPilot — Hệ thống hỗ trợ Da liễu",
  description: "AI Medical Scribe, Clinical Reminder và Patient QnA Chatbot cho Da liễu",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi" suppressHydrationWarning>
      <body suppressHydrationWarning>{children}</body>
    </html>
  );
}
