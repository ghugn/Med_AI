import { apiClient } from "@/lib/api/client";
import { config } from "@/config";
import { generateRequestId } from "@/lib/utils/format";
import { MOCK_REMINDER_RESPONSE } from "./mock/reminder.mock";
import type { ReminderRequest, ReminderResponse, ScribeResponse } from "@/types";

function delay(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

export async function runReminder(
  structuredRecord: ScribeResponse,
  previousRecords?: ScribeResponse[]
): Promise<ReminderResponse> {
  const body: ReminderRequest = {
    request_id: generateRequestId("req_reminder"),
    module: "clinical_reminder",
    schema_version: config.schemaVersion,
    structured_record: structuredRecord,
    previous_records: previousRecords,
  };

  if (config.mockApi) {
    await delay(1600);
    return { ...MOCK_REMINDER_RESPONSE, request_id: body.request_id! };
  }

  return apiClient.post<ReminderResponse, ReminderRequest>(config.api.reminder, body);
}
