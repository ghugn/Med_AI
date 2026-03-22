// ---------------------------------------------------------------------------
// Domain types — mirrors the JSON schemas agreed with the AI engineering team
// ---------------------------------------------------------------------------

// ─── Auth ──────────────────────────────────────────────────────────────────

export type UserRole = "doctor" | "patient";

export interface User {
  id: string;
  name: string;
  role: UserRole;
  department?: string;   // e.g. "Da liễu"
  hospital?: string;
}

// ─── Shared primitives ────────────────────────────────────────────────────

export type ConfidenceLevel = "high" | "medium" | "low";

export interface Patient {
  patient_id: string;
  name: string;
  age: number;
  gender: "Nam" | "Nữ" | "Khác";
  lastVisit?: string;
}

// ─── Feature 1 — Medical Scribe ───────────────────────────────────────────

/** POST /api/scribe  →  ScribeResponse */
export interface ScribeRequest {
  request_id?: string;
  module: "medical_scribe";
  schema_version: string;
  /** "audio" when real STT is wired up; "text" for direct transcript input */
  input_type: "audio" | "text";
  transcript?: string;
  /** base64-encoded audio blob — sent when input_type === "audio" */
  audio_base64?: string;
  patient_info: {
    patient_id: string | null;
    name: string | null;
    age: number | null;
    gender: string | null;
  };
}

export interface ClinicalInfo {
  chief_complaint: string;
  symptoms: string[];
  duration: string;
  onset: string;
  lesion_location: string[];
  lesion_distribution: string;
  itching: boolean | null;
  pain: boolean | null;
  burning: boolean | null;
  scaling: boolean | null;
  blister: boolean | null;
  discharge: boolean | null;
  bleeding: boolean | null;
  spreading_pattern: string;
  trigger_factors: string[];
  previous_treatment: string[];
  history_update: string[];
  allergy_update: string[];
  medication_update: string[];
  current_notes: string;
}

export interface StructuredSummary {
  one_liner: string;
  important_findings: string[];
  negative_findings: string[];
  missing_required_fields: string[];
}

export interface ScribeResponse {
  request_id: string;
  module: "medical_scribe";
  schema_version: string;
  patient_info: ScribeRequest["patient_info"];
  clinical_info: ClinicalInfo;
  structured_summary: StructuredSummary;
  draft_note: string;
  missing_required_fields: string[];
  uncertain_fields: string[];
  requires_doctor_approval: boolean;
  field_confidence: Record<string, number>;
  latency_ms: number;
  model_version: string;
}

// ─── Feature 2 — Clinical Reminder ───────────────────────────────────────

/** POST /api/reminder  →  ReminderResponse */
export interface ReminderRequest {
  request_id?: string;
  module: "clinical_reminder";
  schema_version: string;
  structured_record: ScribeResponse;
  /** Optional: serialized previous visit records for recurrence detection */
  previous_records?: ScribeResponse[];
}

export interface ReminderResponse {
  request_id: string;
  module: "clinical_reminder";
  missing_critical_info: string[];
  questions_to_ask: string[];
  red_flags: string[];
  possible_considerations: string[];
  suggested_next_checks: string[];
  guideline_evidence: string[];
  latency_ms: number;
  model_version: string;
}

// ─── Feature 3 — Patient QnA Chatbot ─────────────────────────────────────

/** POST /api/chat  →  ChatResponse */
export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatRequest {
  request_id?: string;
  module: "patient_derma_qna";
  schema_version: string;
  user_role: "patient";
  question: string;
  /** Full conversation history for multi-turn context */
  history: ChatMessage[];
  language: "vi" | "en";
  /** base64 image — for future image-upload expansion */
  image_base64?: string;
}

export interface ChatResponse {
  request_id: string;
  module: "patient_derma_qna";
  schema_version: string;
  user_role: "patient";
  question: string;
  answer: string;
  safety_notice: string;
  possible_topics: string[];
  when_to_seek_care: string[];
  red_flag_advice: string[];
  source_evidence: string[];
  confidence_level: ConfidenceLevel;
  requires_doctor_followup: boolean;
  requires_emergency_care: boolean;
  latency_ms: number;
  model_version: string;
}

// ─── UI-only types ────────────────────────────────────────────────────────

/** Chat message as displayed in the UI (extends ChatMessage with metadata) */
export interface UIChatMessage extends ChatMessage {
  id: string;
  timestamp: Date;
  meta?: Omit<ChatResponse, "request_id" | "module" | "schema_version" | "user_role" | "question" | "answer" | "latency_ms" | "model_version">;
  isLoading?: boolean;
}
