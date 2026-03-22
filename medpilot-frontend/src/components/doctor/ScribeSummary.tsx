import { Card, SectionLabel, Badge, AlertBanner, ConfidenceBar } from "@/components/ui";
import type { ScribeResponse } from "@/types";

interface ScribeSummaryProps {
  result: ScribeResponse;
  draftNote: string;
  onDraftChange: (v: string) => void;
  onSave: () => void;
}

export function ScribeSummary({ result, draftNote, onDraftChange, onSave }: ScribeSummaryProps) {
  const { structured_summary, uncertain_fields, field_confidence } = result;

  return (
    <div className="flex flex-col gap-4">
      {/* One-liner */}
      <Card>
        <SectionLabel>Tóm tắt ca khám</SectionLabel>
        <p className="text-sm leading-relaxed text-gray-700 dark:text-gray-300">
          {structured_summary.one_liner}
        </p>

        <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Positive findings */}
          <div>
            <SectionLabel>Phát hiện dương tính</SectionLabel>
            <ul className="flex flex-col gap-1.5">
              {structured_summary.important_findings.map((f, i) => (
                <li key={i} className="flex gap-2 text-sm text-gray-700 dark:text-gray-300">
                  <CheckIcon />
                  <span>{f}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Negative findings */}
          <div>
            <SectionLabel>Phát hiện âm tính</SectionLabel>
            <ul className="flex flex-col gap-1">
              {structured_summary.negative_findings.map((f, i) => (
                <li key={i} className="text-sm text-gray-400 dark:text-gray-500">— {f}</li>
              ))}
            </ul>
          </div>
        </div>
      </Card>

      {/* Uncertain fields warning */}
      {uncertain_fields.length > 0 && (
        <AlertBanner variant="warning" title="Thông tin chưa chắc chắn — cần xác nhận lại">
          <p className="mt-0.5">{uncertain_fields.join(", ")}</p>
        </AlertBanner>
      )}

      {/* Confidence scores */}
      <Card>
        <SectionLabel>Độ tin cậy từng trường</SectionLabel>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-3">
          {Object.entries(field_confidence).map(([key, val]) => (
            <ConfidenceBar key={key} label={key} value={val} />
          ))}
        </div>
      </Card>

      {/* Draft note editor */}
      <Card>
        <div className="flex items-center justify-between mb-3">
          <SectionLabel>Ghi chú nháp — Bác sĩ kiểm tra &amp; chỉnh sửa</SectionLabel>
          <Badge variant="warning">Chờ duyệt</Badge>
        </div>

        <textarea
          value={draftNote}
          onChange={(e) => onDraftChange(e.target.value)}
          rows={8}
          className="w-full text-sm leading-relaxed resize-y rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 p-3 text-gray-800 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-200 dark:focus:ring-blue-800 transition"
        />

        <div className="flex gap-2 mt-3">
          <button
            onClick={onSave}
            className="flex-1 flex items-center justify-center gap-2 text-sm font-medium py-2 rounded-lg bg-blue-50 text-blue-700 border border-blue-200 hover:bg-blue-100 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-800 transition-colors"
          >
            <ClipboardIcon />
            Lưu vào hồ sơ
          </button>
          <button className="px-4 text-sm text-gray-500 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
            Chỉnh sửa
          </button>
        </div>
      </Card>
    </div>
  );
}

function CheckIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"
      strokeLinecap="round" strokeLinejoin="round" className="text-green-500 mt-0.5 shrink-0">
      <path d="M20 6L9 17l-5-5" />
    </svg>
  );
}

function ClipboardIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
      strokeLinecap="round" strokeLinejoin="round">
      <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2M9 2h6v4H9zM9 12h6M9 16h4" />
    </svg>
  );
}
