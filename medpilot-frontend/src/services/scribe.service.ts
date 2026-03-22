/**
 * Scribe Service
 * ──────────────
 * Swap NEXT_PUBLIC_MOCK_API=false to hit the real AI endpoint.
 * The AI engineer only needs to match the ScribeRequest / ScribeResponse contract.
 */

import { apiClient } from "@/lib/api/client";
import { config } from "@/config";
import { generateRequestId } from "@/lib/utils/format";
import { MOCK_SCRIBE_RESPONSE } from "./mock/scribe.mock";
import type { ScribeRequest, ScribeResponse } from "@/types";

function delay(ms: number) {
  return new Promise((r) => setTimeout(r, ms));
}

export async function runScribe(
  payload: Omit<ScribeRequest, "request_id" | "module" | "schema_version">
): Promise<ScribeResponse> {
  const body: ScribeRequest = {
    ...payload,
    request_id: generateRequestId("req_scribe"),
    module: "medical_scribe",
    schema_version: config.schemaVersion,
  };

  if (config.mockApi) {
    // Simulate network + AI processing latency
    await delay(2200);
    return { ...MOCK_SCRIBE_RESPONSE, request_id: body.request_id! };
  }

  return apiClient.post<ScribeResponse, ScribeRequest>(config.api.scribe, body);
}

export async function saveScribeRecord(patientData: any, draftNote: string, scribeSummary?: any): Promise<boolean> {
  try {
    // 1. Tạo case mới bên medpilot-core (port 8000)
    const createRes = await fetch("http://localhost:8000/api/v1/cases/create", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ho_ten: patientData.ho_ten || "Bệnh nhân mới",
        tuoi: patientData.tuoi || 30,
        gioi_tinh: patientData.gioi_tinh || "Nam",
        bac_si_id: "BS_01",
        trieu_chung_transcript: "Bản nháp lưu từ Scribe"
      }),
    });
    
    if (!createRes.ok) throw new Error("Không thể tạo case mới");
    const createData = await createRes.json();
    const caseId = createData.data?.case_id;
    
    if (!caseId) throw new Error("Không nhận được case_id từ server");

    // Parse AI metrics for the DB
    let redFlags = "Không có báo động đỏ";
    let uncertaintyScore = 0.0;
    
    if (scribeSummary) {
      if (scribeSummary.missing_required_fields && scribeSummary.missing_required_fields.length > 0) {
        redFlags = "Thiếu thông tin: " + scribeSummary.missing_required_fields.join(", ");
      }
      if (scribeSummary.field_confidence) {
        const confidences = Object.values(scribeSummary.field_confidence) as number[];
        if (confidences.length > 0) {
          const avgConf = confidences.reduce((a, b) => a + b, 0) / confidences.length;
          uncertaintyScore = parseFloat((1.0 - avgConf).toFixed(2)); // Điểm rủi ro = 1 - độ tự tin
        }
      }
    }

    // 2. Lưu Draft Note vào case vừa tạo (bước doctor-approve)
    const approveRes = await fetch(`http://localhost:8000/api/v1/cases/${caseId}/doctor-approve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        draft_note: draftNote,
        spo2: null,
        hr: null,
        bp: null,
        red_flags: redFlags,
        uncertainty_score: uncertaintyScore
      }),
    });

    if (!approveRes.ok) throw new Error("Không thể lưu draft note");
    return true;
  } catch (error) {
    console.error("Lỗi khi lưu vào hồ sơ (Excel):", error);
    return false;
  }
}

