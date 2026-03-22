"use client";

import { useEffect, useRef } from "react";
import { ChatBubble } from "./ChatBubble";
import type { UIChatMessage } from "@/types";

interface ChatWindowProps {
  messages: UIChatMessage[];
}

export function ChatWindow({ messages }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-5 flex flex-col gap-4">
      {messages.map((msg) => (
        <ChatBubble key={msg.id} message={msg} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
