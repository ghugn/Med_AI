import { useCallback, useRef } from "react";
import { useChatStore } from "@/stores/chat.store";
import { sendChatMessage } from "@/services/chat.service";
import { generateRequestId } from "@/lib/utils/format";
import type { ChatMessage, UIChatMessage } from "@/types";

export function useChat() {
  const store = useChatStore();
  const abortRef = useRef<AbortController | null>(null);

  // Build ChatMessage history from UI messages (strips UI-only fields)
  const getHistory = useCallback((): ChatMessage[] =>
    store.messages
      .filter((m) => !m.isLoading)
      .map((m) => ({ role: m.role, content: m.content })),
  [store.messages]);

  const sendMessage = useCallback(async (question: string) => {
    if (!question.trim() || store.isLoading) return;

    // Add user message
    const userMsg: UIChatMessage = {
      id: generateRequestId("msg"),
      role: "user",
      content: question,
      timestamp: new Date(),
    };
    store.addMessage(userMsg);

    // Add placeholder for assistant
    const assistantId = generateRequestId("msg");
    const placeholderMsg: UIChatMessage = {
      id: assistantId,
      role: "assistant",
      content: "",
      timestamp: new Date(),
      isLoading: true,
    };
    store.addMessage(placeholderMsg);
    store.setLoading(true);

    abortRef.current?.abort();
    abortRef.current = new AbortController();

    try {
      const history = getHistory();
      const response = await sendChatMessage(question, history, abortRef.current.signal);

      store.updateMessage(assistantId, {
        content: response.answer,
        isLoading: false,
        meta: {
          safety_notice: response.safety_notice,
          possible_topics: response.possible_topics,
          when_to_seek_care: response.when_to_seek_care,
          red_flag_advice: response.red_flag_advice,
          source_evidence: response.source_evidence,
          confidence_level: response.confidence_level,
          requires_doctor_followup: response.requires_doctor_followup,
          requires_emergency_care: response.requires_emergency_care,
        },
      });
    } catch (err) {
      if ((err as Error).name === "AbortError") return;
      store.updateMessage(assistantId, {
        content: "Xin lỗi, đã xảy ra lỗi. Vui lòng thử lại.",
        isLoading: false,
      });
    } finally {
      store.setLoading(false);
    }
  }, [store, getHistory]);

  return { ...store, sendMessage };
}
