"use client";

import { useState, useRef, type KeyboardEvent } from "react";
import { cn } from "@/lib/utils/cn";

const QUICK_PROMPTS = [
  "Da tay bị nổi đỏ ngứa là bệnh gì?",
  "Dấu hiệu nhiễm nấm da?",
  "Khi nào cần đi khám gấp?",
  "Kem bôi da nào an toàn?",
  "Viêm da tiếp xúc là gì?",
];

interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  function handleSend() {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
    // Reset textarea height
    if (textareaRef.current) textareaRef.current.style.height = "auto";
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function handleInput() {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }

  function handleQuickPrompt(prompt: string) {
    setValue(prompt);
    textareaRef.current?.focus();
  }

  const canSend = value.trim().length > 0 && !disabled;

  return (
    <div className="bg-white dark:bg-gray-950 border-t border-gray-100 dark:border-gray-800">
      {/* Quick prompts */}
      <div className="px-4 pt-3 pb-1 flex gap-2 overflow-x-auto scrollbar-hide">
        {QUICK_PROMPTS.map((p) => (
          <button
            key={p}
            onClick={() => handleQuickPrompt(p)}
            disabled={disabled}
            className="shrink-0 text-xs text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full px-3 py-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors disabled:opacity-40"
          >
            {p}
          </button>
        ))}
      </div>

      {/* Input row */}
      <div className="px-4 pb-4 pt-2 flex items-end gap-2">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          onInput={handleInput}
          rows={1}
          placeholder="Hỏi về vấn đề da liễu của bạn..."
          disabled={disabled}
          className={cn(
            "flex-1 resize-none text-sm rounded-xl border border-gray-200 dark:border-gray-700",
            "bg-gray-50 dark:bg-gray-800 text-gray-800 dark:text-gray-200",
            "px-4 py-2.5 leading-relaxed",
            "focus:outline-none focus:ring-2 focus:ring-blue-200 dark:focus:ring-blue-800",
            "placeholder:text-gray-400 transition",
            "disabled:opacity-50"
          )}
        />
        <button
          onClick={handleSend}
          disabled={!canSend}
          className={cn(
            "shrink-0 w-10 h-10 rounded-xl flex items-center justify-center transition-all",
            canSend
              ? "bg-blue-600 text-white hover:bg-blue-700 active:scale-95"
              : "bg-gray-100 dark:bg-gray-800 text-gray-300 dark:text-gray-600 cursor-not-allowed"
          )}
        >
          <SendIcon />
        </button>
      </div>
    </div>
  );
}

function SendIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
    </svg>
  );
}
