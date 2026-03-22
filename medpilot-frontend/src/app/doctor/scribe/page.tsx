"use client";

import { Card, SectionLabel, Badge } from "@/components/ui";
import { RecordingControls, ScribeSummary } from "@/components/doctor";
import { useScribe } from "@/hooks/useScribe";
import { AlertBanner } from "@/components/ui";
import { useState } from "react";
import { saveScribeRecord } from "@/services/scribe.service";

const MOCK_PATIENTS = [
  { id: "P000", label: "— Bệnh nhân mới —", ho_ten: "Bệnh nhân mới", tuoi: 30, gioi_tinh: "Nam" },
  { id: "P001", label: "Nguyễn Văn An — 28t, Nam (khám: 15/03/2025)", ho_ten: "Nguyễn Văn An", tuoi: 28, gioi_tinh: "Nam" },
  { id: "P002", label: "Trần Thị Bình — 34t, Nữ (khám: 10/03/2025)", ho_ten: "Trần Thị Bình", tuoi: 34, gioi_tinh: "Nữ" },
  { id: "P003", label: "Lê Minh Cường — 45t, Nam (khám: 05/03/2025)", ho_ten: "Lê Minh Cường", tuoi: 45, gioi_tinh: "Nam" },
];

export default function ScribePage() {
  const {
    recordingState,
    elapsed,
    result,
    draftNote,
    error,
    setDraftNote,
    startRecording,
    stopRecording,
    reset,
  } = useScribe();

  const [selectedPatientId, setSelectedPatientId] = useState(MOCK_PATIENTS[0].id);
  const [isSaving, setIsSaving] = useState(false);

  async function handleSave() {
    if (!draftNote) {
      alert("Hồ sơ trống, không có gì để lưu.");
      return;
    }
    setIsSaving(true);
    const patientData = MOCK_PATIENTS.find(p => p.id === selectedPatientId) || MOCK_PATIENTS[0];
    const success = await saveScribeRecord(patientData, draftNote, result);
    setIsSaving(false);

    if (success) {
      alert("Đã lưu thành công vào hồ sơ Excel của hệ thống Triage!");
    } else {
      alert("Không thể lưu vào hồ sơ lúc này. Vui lòng xem console báo lỗi.");
    }
  }

  return (
    <div className="flex flex-col gap-5">
      {/* Control card */}
      <Card>
        <div className="flex items-start justify-between gap-3 mb-4">
          <div>
            <h2 className="text-lg font-medium text-gray-900 dark:text-gray-100">AI Medical Scribe</h2>
            <p className="text-sm text-gray-400 mt-0.5">
              Ghi âm hội thoại khám bệnh → Hồ sơ có cấu trúc
            </p>
          </div>
          <StatusBadge state={recordingState} />
        </div>

        {/* Patient selector */}
        <div className="mb-4">
          <SectionLabel>Chọn bệnh nhân</SectionLabel>
          <select 
            className="w-full text-sm rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 px-3 py-2 text-gray-800 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-200 dark:focus:ring-blue-800"
            value={selectedPatientId}
            onChange={(e) => setSelectedPatientId(e.target.value)}
          >
            {MOCK_PATIENTS.map((p) => (
              <option key={p.id} value={p.id}>{p.label}</option>
            ))}
          </select>
        </div>

        <RecordingControls
          state={recordingState}
          elapsed={elapsed}
          onStart={startRecording}
          onStop={() => stopRecording()}
          onReset={reset}
        />
      </Card>

      {/* Error state */}
      {error && (
        <AlertBanner variant="danger" title="Lỗi xử lý">
          {error}
        </AlertBanner>
      )}

      {/* Results */}
      {result && (
        <ScribeSummary
          result={result}
          draftNote={draftNote}
          onDraftChange={setDraftNote}
          onSave={handleSave}
        />
      )}
    </div>
  );
}

function StatusBadge({ state }: { state: string }) {
  const map: Record<string, { label: string; variant: "default" | "danger" | "warning" | "success" | "info" }> = {
    idle:       { label: "Sẵn sàng",    variant: "default" },
    recording:  { label: "● Đang ghi",  variant: "danger" },
    processing: { label: "Xử lý...",    variant: "warning" },
    done:       { label: "Hoàn tất",    variant: "success" },
    error:      { label: "Lỗi",         variant: "danger" },
  };
  const { label, variant } = map[state] ?? map.idle;
  return <Badge variant={variant}>{label}</Badge>;
}
