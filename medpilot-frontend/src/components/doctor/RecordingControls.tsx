"use client";

import { Button } from "@/components/ui";
import { formatDuration } from "@/lib/utils/format";

interface RecordingControlsProps {
  state: "idle" | "recording" | "processing" | "done" | "error";
  elapsed: number;
  onStart: () => void;
  onStop: () => void;
  onReset: () => void;
}

export function RecordingControls({ state, elapsed, onStart, onStop, onReset }: RecordingControlsProps) {
  return (
    <div className="flex items-center gap-3 flex-wrap">
      {state === "idle" && (
        <Button variant="danger" onClick={onStart} icon={<MicIcon />}>
          Bắt đầu ghi âm
        </Button>
      )}

      {state === "recording" && (
        <>
          <Button variant="secondary" onClick={onStop} icon={<StopIcon />}>
            Dừng ghi âm
          </Button>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
            <span className="text-sm font-mono text-red-600 dark:text-red-400 tabular-nums">
              {formatDuration(elapsed)}
            </span>
          </div>
        </>
      )}

      {state === "processing" && (
        <Button variant="secondary" loading>
          Đang phân tích transcript...
        </Button>
      )}

      {(state === "done" || state === "error") && (
        <button
          onClick={onReset}
          className="text-sm text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
        >
          ← Ghi âm mới
        </button>
      )}
    </div>
  );
}

function MicIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3zM19 10v2a7 7 0 0 1-14 0v-2M12 19v4M8 23h8" />
    </svg>
  );
}

function StopIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="8" y="5" width="8" height="14" />
    </svg>
  );
}
