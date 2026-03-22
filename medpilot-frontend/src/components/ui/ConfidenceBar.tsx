import { cn } from "@/lib/utils/cn";

interface ConfidenceBarProps {
  value: number; // 0–1
  label?: string;
  showPercent?: boolean;
}

function getColorClass(v: number) {
  if (v >= 0.8) return "bg-green-500";
  if (v >= 0.55) return "bg-amber-500";
  return "bg-red-500";
}

function getTextClass(v: number) {
  if (v >= 0.8) return "text-green-600 dark:text-green-400";
  if (v >= 0.55) return "text-amber-600 dark:text-amber-400";
  return "text-red-600 dark:text-red-400";
}

export function ConfidenceBar({ value, label, showPercent = true }: ConfidenceBarProps) {
  const pct = Math.round(value * 100);
  return (
    <div className="flex flex-col gap-1">
      {label && (
        <span className="text-xs text-gray-500 dark:text-gray-400 truncate">{label}</span>
      )}
      <div className="flex items-center gap-2">
        <div className="flex-1 h-1 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
          <div
            className={cn("h-full rounded-full transition-all duration-700", getColorClass(value))}
            style={{ width: `${pct}%` }}
          />
        </div>
        {showPercent && (
          <span className={cn("text-xs font-medium min-w-[28px] text-right tabular-nums", getTextClass(value))}>
            {pct}%
          </span>
        )}
      </div>
    </div>
  );
}
