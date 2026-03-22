/**
 * POST /api/scribe
 * ─────────────────────────────────────────────────────────────────────────────
 * Integration boundary between frontend and AI service.
 *
 * In production, set BACKEND_URL to the AI engineer's FastAPI/Flask server.
 * next.config.ts already rewrites /api/* → BACKEND_URL/api/* so this route
 * is only reached when BACKEND_URL is not set (i.e. during local dev without
 * a running backend).
 *
 * To test against the real AI service, set BACKEND_URL in .env.local.
 * ─────────────────────────────────────────────────────────────────────────────
 */

import { NextRequest, NextResponse } from "next/server";
import type { ScribeRequest, ScribeResponse } from "@/types";
import { MOCK_SCRIBE_RESPONSE } from "@/services/mock/scribe.mock";

export async function POST(req: NextRequest) {
  const body: ScribeRequest = await req.json();

  // ── Forward to real AI service when BACKEND_URL is configured ─────────────
  const backendUrl = process.env.BACKEND_URL;
  if (backendUrl) {
    const upstream = await fetch(`${backendUrl}/api/scribe`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await upstream.json();
    return NextResponse.json(data, { status: upstream.status });
  }

  // ── Mock fallback (no backend configured) ─────────────────────────────────
  await new Promise((r) => setTimeout(r, 200)); // simulate latency
  const response: ScribeResponse = {
    ...MOCK_SCRIBE_RESPONSE,
    request_id: body.request_id ?? "req_scribe_fallback",
    latency_ms: 200,
  };

  return NextResponse.json(response);
}
