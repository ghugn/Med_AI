"use client";

import { Card, SectionLabel, Button, AlertBanner } from "@/components/ui";
import { ReminderPanel } from "@/components/doctor";
import { useReminder } from "@/hooks/useReminder";

export default function ReminderPage() {
  const { loading, result, error, hasRecord, trigger, reset } = useReminder();

  return (
    <div className="flex flex-col gap-5">
      {/* Control card */}
      <Card>
        <h2 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-1">
          AI Clinical Reminder
        </h2>
        <p className="text-sm text-gray-400 mb-4">
          Phân tích hồ sơ từ Medical Scribe → Nhắc nhở và gợi ý lâm sàng
        </p>

        {/* Current record preview */}
        <div className="rounded-lg bg-gray-50 dark:bg-gray-800 border border-gray-100 dark:border-gray-700 p-3 mb-4">
          <SectionLabel>Hồ sơ đang phân tích</SectionLabel>
          {hasRecord ? (
            <p className="text-sm text-gray-700 dark:text-gray-300">
              Ban đỏ ngứa hai bàn tay · 2 tuần · Tiền sử viêm da cơ địa · Tiếp xúc nước rửa chén
            </p>
          ) : (
            <p className="text-sm text-gray-400 italic">
              Chưa có hồ sơ. Vui lòng chạy Medical Scribe trước.
            </p>
          )}
        </div>

        <div className="flex gap-2">
          <Button
            variant="primary"
            loading={loading}
            disabled={!hasRecord}
            icon={<BrainIcon />}
            onClick={trigger}
          >
            Chạy AI Reminder
          </Button>
          {result && (
            <Button variant="ghost" onClick={reset}>
              Xóa kết quả
            </Button>
          )}
        </div>
      </Card>

      {/* Error */}
      {error && (
        <AlertBanner variant="danger" title="Lỗi phân tích">
          {error}
        </AlertBanner>
      )}

      {/* Results */}
      {result && <ReminderPanel result={result} />}
    </div>
  );
}

function BrainIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
      strokeLinecap="round" strokeLinejoin="round">
      <path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2" />
    </svg>
  );
}
