import { Card, SectionLabel, Badge } from "@/components/ui";
import type { ReminderResponse } from "@/types";

interface ReminderPanelProps {
  result: ReminderResponse;
}

const SECTIONS = [
  { key: "missing_critical_info",   label: "Thông tin còn thiếu",       variant: "danger"  as const },
  { key: "questions_to_ask",        label: "Câu hỏi nên hỏi thêm",      variant: "info"    as const },
  { key: "red_flags",               label: "Dấu hiệu cần chú ý",        variant: "warning" as const },
  { key: "possible_considerations", label: "Hướng cân nhắc (hỗ trợ)",   variant: "success" as const },
  { key: "suggested_next_checks",   label: "Gợi ý bước tiếp theo",      variant: "default" as const },
] as const;

export function ReminderPanel({ result }: ReminderPanelProps) {
  return (
    <div className="flex flex-col gap-4">
      {SECTIONS.map(({ key, label, variant }) => {
        const items = result[key];
        if (!items.length) return null;
        return (
          <Card key={key}>
            <div className="flex items-center gap-2 mb-3">
              <SectionLabel>{label}</SectionLabel>
              <Badge variant={variant}>{items.length}</Badge>
            </div>
            <ul className="flex flex-col gap-2">
              {items.map((item, i) => (
                <li key={i} className="text-sm text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-800 rounded-lg px-3 py-2 leading-relaxed">
                  {item}
                </li>
              ))}
            </ul>
          </Card>
        );
      })}

      {/* Guideline evidence */}
      {result.guideline_evidence.length > 0 && (
        <Card className="border-l-4 border-l-blue-400 rounded-l-none">
          <SectionLabel>Bằng chứng / Guideline (RAG)</SectionLabel>
          <ul className="flex flex-col gap-2">
            {result.guideline_evidence.map((e, i) => (
              <li key={i} className="text-xs text-gray-500 dark:text-gray-400 leading-relaxed">
                {e}
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  );
}
