import { apiClient } from "@/lib/api/client";
import { config } from "@/config";
import { generateRequestId } from "@/lib/utils/format";
import { buildMockChatResponse, buildMockEmergencyResponse } from "./mock/chat.mock";
import type { ChatMessage, ChatRequest, ChatResponse } from "@/types";

function delay(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

// Simple keyword check to return emergency mock for demo purposes
const EMERGENCY_KEYWORDS = ["khó thở", "phù", "ngất", "sốc", "lan nhanh toàn thân"];

export async function sendChatMessage(
  question: string,
  history: ChatMessage[],
  signal?: AbortSignal
): Promise<ChatResponse> {
  const body: ChatRequest = {
    request_id: generateRequestId("req_chat"),
    module: "patient_derma_qna",
    schema_version: "1.0",
    user_role: "patient",
    question,
    history,
    language: "vi",
  };

  if (config.mockApi) {
    await delay(1400);
    const isEmergency = EMERGENCY_KEYWORDS.some((kw) =>
      question.toLowerCase().includes(kw)
    );
    return isEmergency
      ? buildMockEmergencyResponse(question)
      : buildMockChatResponse(question);
  }

  return apiClient.post<ChatResponse, ChatRequest>(config.api.chat, body, { signal });
}
