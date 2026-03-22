/**
 * POST /api/chat
 * ─────────────────────────────────────────────────────────────────────────────
 * Accepts a ChatRequest, forwards to the AI service (patient QnA),
 * returns ChatResponse.
 *
 * The AI service is responsible for RAG retrieval from the dermatology
 * knowledge base and response generation.
 * ─────────────────────────────────────────────────────────────────────────────
 */

import { NextRequest, NextResponse } from "next/server";
import type { ChatRequest, ChatResponse } from "@/types";
import { buildMockChatResponse } from "@/services/mock/chat.mock";

export async function POST(req: NextRequest) {
  const body: ChatRequest = await req.json();

  const backendUrl = process.env.BACKEND_URL;
  if (backendUrl) {
    const upstream = await fetch(`${backendUrl}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await upstream.json();
    return NextResponse.json(data, { status: upstream.status });
  }

  await new Promise((r) => setTimeout(r, 120));
  const response: ChatResponse = {
    ...buildMockChatResponse(body.question),
    request_id: body.request_id ?? "req_chat_fallback",
    latency_ms: 120,
  };

  return NextResponse.json(response);
}
