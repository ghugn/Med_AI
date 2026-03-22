"use client";

import { useEffect } from "react";
import { ChatWindow, ChatInput } from "@/components/patient";
import { useChatStore } from "@/stores/chat.store";
import { useChat } from "@/hooks/useChat";
import { generateRequestId } from "@/lib/utils/format";
import type { UIChatMessage } from "@/types";

const WELCOME_MESSAGE: UIChatMessage = {
  id: "welcome",
  role: "assistant",
  content:
    "Xin chào! Tôi là trợ lý Da liễu AI. Bạn có thể hỏi tôi về các vấn đề da như: mụn, eczema, vảy nến, nấm da, dị ứng da... Lưu ý: câu trả lời chỉ mang tính tham khảo, không thay thế khám bác sĩ.",
  timestamp: new Date(),
};

export default function ChatPage() {
  const { messages, isLoading, sendMessage } = useChat();
  const addMessage = useChatStore((s) => s.addMessage);

  // Seed welcome message only once
  useEffect(() => {
    if (messages.length === 0) {
      addMessage({ ...WELCOME_MESSAGE, id: generateRequestId("welcome") });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <>
      <ChatWindow messages={messages} />
      <ChatInput onSend={sendMessage} disabled={isLoading} />
    </>
  );
}
