/**
 * POST /api/reminder
 * ─────────────────────────────────────────────────────────────────────────────
 * Accepts a ReminderRequest (contains the full ScribeResponse + optional
 * previous_records), forwards to the AI service, returns ReminderResponse.
 * ─────────────────────────────────────────────────────────────────────────────
 */

import { NextRequest, NextResponse } from "next/server";
import type { ReminderRequest, ReminderResponse } from "@/types";
import { MOCK_REMINDER_RESPONSE } from "@/services/mock/reminder.mock";

export async function POST(req: NextRequest) {
  const body: ReminderRequest = await req.json();

  const backendUrl = process.env.BACKEND_URL;
  if (backendUrl) {
    const upstream = await fetch(`${backendUrl}/api/reminder`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await upstream.json();
    return NextResponse.json(data, { status: upstream.status });
  }

  await new Promise((r) => setTimeout(r, 150));
  const response: ReminderResponse = {
    ...MOCK_REMINDER_RESPONSE,
    request_id: body.request_id ?? "req_reminder_fallback",
    latency_ms: 150,
  };

  return NextResponse.json(response);
}
