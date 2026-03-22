import { cn } from "@/lib/utils/cn";
import { Badge, AlertBanner } from "@/components/ui";
import type { UIChatMessage } from "@/types";

interface ChatBubbleProps {
  message: UIChatMessage;
}

export function ChatBubble({ message }: ChatBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={cn("flex flex-col gap-2", isUser ? "items-end" : "items-start")}>
      {/* Bubble */}
      <div className={cn(
        "max-w-[80%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed",
        isUser
          ? "bg-blue-50 text-blue-900 border border-blue-100 dark:bg-blue-900/40 dark:text-blue-100 dark:border-blue-800"
          : "bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200 border border-gray-100 dark:border-gray-800",
        message.isLoading && "animate-pulse"
      )}>
        {message.isLoading ? (
          <span className="text-gray-400">AI đang soạn câu trả lời...</span>
        ) : (
          message.content
        )}
      </div>

      {/* Metadata cards — only for non-loading assistant messages */}
      {!isUser && !message.isLoading && message.meta && (
        <div className="max-w-[80%] flex flex-col gap-2">
          {/* Confidence + follow-up badges */}
          <div className="flex gap-2 flex-wrap">
            <Badge variant={
              message.meta.confidence_level === "high" ? "success" :
              message.meta.confidence_level === "low" ? "danger" : "warning"
            }>
              Độ tin cậy: {message.meta.confidence_level}
            </Badge>
            {message.meta.requires_doctor_followup && (
              <Badge variant="info">Nên gặp bác sĩ</Badge>
            )}
            {message.meta.requires_emergency_care && (
              <Badge variant="danger">⚠ Khẩn cấp</Badge>
            )}
          </div>

          {/* Possible topics */}
          {message.meta.possible_topics.length > 0 && (
            <div className="bg-gray-50 dark:bg-gray-800/60 border border-gray-100 dark:border-gray-700 rounded-xl p-3">
              <p className="text-[10px] font-semibold uppercase tracking-widest text-gray-400 mb-2">
                Chủ đề liên quan
              </p>
              <div className="flex flex-wrap gap-1.5">
                {message.meta.possible_topics.map((t) => (
                  <Badge key={t}>{t}</Badge>
                ))}
              </div>
            </div>
          )}

          {/* When to seek care */}
          {message.meta.when_to_seek_care.length > 0 && (
            <AlertBanner variant="warning" title="Khi nào cần khám bác sĩ">
              <ul className="mt-1 flex flex-col gap-0.5">
                {message.meta.when_to_seek_care.map((w, i) => (
                  <li key={i}>• {w}</li>
                ))}
              </ul>
            </AlertBanner>
          )}

          {/* Red flags */}
          {message.meta.red_flag_advice.length > 0 && (
            <AlertBanner variant="danger" title="Cảnh báo">
              <ul className="mt-1 flex flex-col gap-0.5">
                {message.meta.red_flag_advice.map((r, i) => (
                  <li key={i}>⚠ {r}</li>
                ))}
              </ul>
            </AlertBanner>
          )}

          {/* Safety notice */}
          <p className="text-[11px] text-gray-400 italic">{message.meta.safety_notice}</p>
        </div>
      )}
    </div>
  );
}
