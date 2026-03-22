"""
Pydantic schemas — mirrors the frontend's TypeScript types exactly.
3 features: Medical Scribe, Clinical Reminder, Patient QnA Chat.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Literal


# ═══════════════════════════════════════════════════════════════════════════════
# Feature 1 — Medical Scribe
# ═══════════════════════════════════════════════════════════════════════════════

class PatientInfo(BaseModel):
    patient_id: Optional[str] = None
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None


class ClinicalInfo(BaseModel):
    chief_complaint: str = ""
    symptoms: List[str] = Field(default_factory=list)
    duration: str = ""
    onset: str = ""
    lesion_location: List[str] = Field(default_factory=list)
    lesion_distribution: str = ""
    itching: Optional[bool] = None
    pain: Optional[bool] = None
    burning: Optional[bool] = None
    scaling: Optional[bool] = None
    blister: Optional[bool] = None
    discharge: Optional[bool] = None
    bleeding: Optional[bool] = None
    spreading_pattern: str = ""
    trigger_factors: List[str] = Field(default_factory=list)
    previous_treatment: List[str] = Field(default_factory=list)
    history_update: List[str] = Field(default_factory=list)
    allergy_update: List[str] = Field(default_factory=list)
    medication_update: List[str] = Field(default_factory=list)
    current_notes: str = ""


class StructuredSummary(BaseModel):
    one_liner: str = ""
    important_findings: List[str] = Field(default_factory=list)
    negative_findings: List[str] = Field(default_factory=list)
    missing_required_fields: List[str] = Field(default_factory=list)


class ScribeRequest(BaseModel):
    request_id: Optional[str] = None
    module: Literal["medical_scribe"] = "medical_scribe"
    schema_version: str = "0.1"
    input_type: Literal["audio", "text"] = "text"
    transcript: Optional[str] = None
    audio_base64: Optional[str] = None
    patient_info: PatientInfo = Field(default_factory=PatientInfo)


class ScribeResponse(BaseModel):
    request_id: str
    module: Literal["medical_scribe"] = "medical_scribe"
    schema_version: str = "0.1"
    patient_info: PatientInfo
    clinical_info: ClinicalInfo
    structured_summary: StructuredSummary
    draft_note: str = ""
    missing_required_fields: List[str] = Field(default_factory=list)
    uncertain_fields: List[str] = Field(default_factory=list)
    requires_doctor_approval: bool = True
    field_confidence: Dict[str, float] = Field(default_factory=dict)
    latency_ms: float = 0
    model_version: str = "scribe_v1"


# ═══════════════════════════════════════════════════════════════════════════════
# Feature 2 — Clinical Reminder
# ═══════════════════════════════════════════════════════════════════════════════

class ReminderRequest(BaseModel):
    request_id: Optional[str] = None
    module: Literal["clinical_reminder"] = "clinical_reminder"
    schema_version: str = "0.1"
    structured_record: ScribeResponse
    previous_records: Optional[List[ScribeResponse]] = None


class ReminderResponse(BaseModel):
    request_id: str
    module: Literal["clinical_reminder"] = "clinical_reminder"
    missing_critical_info: List[str] = Field(default_factory=list)
    questions_to_ask: List[str] = Field(default_factory=list)
    red_flags: List[str] = Field(default_factory=list)
    possible_considerations: List[str] = Field(default_factory=list)
    suggested_next_checks: List[str] = Field(default_factory=list)
    guideline_evidence: List[str] = Field(default_factory=list)
    latency_ms: float = 0
    model_version: str = "reminder_v1"


# ═══════════════════════════════════════════════════════════════════════════════
# Feature 3 — Patient QnA Chatbot
# ═══════════════════════════════════════════════════════════════════════════════

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    request_id: Optional[str] = None
    module: Literal["patient_derma_qna"] = "patient_derma_qna"
    schema_version: str = "1.0"
    user_role: Literal["patient"] = "patient"
    question: str
    history: List[ChatMessage] = Field(default_factory=list)
    language: Literal["vi", "en"] = "vi"
    image_base64: Optional[str] = None


class ChatResponse(BaseModel):
    request_id: str
    module: Literal["patient_derma_qna"] = "patient_derma_qna"
    schema_version: str = "1.0"
    user_role: Literal["patient"] = "patient"
    question: str
    answer: str
    safety_notice: str = ""
    possible_topics: List[str] = Field(default_factory=list)
    when_to_seek_care: List[str] = Field(default_factory=list)
    red_flag_advice: List[str] = Field(default_factory=list)
    source_evidence: List[str] = Field(default_factory=list)
    confidence_level: Literal["high", "medium", "low"] = "medium"
    requires_doctor_followup: bool = True
    requires_emergency_care: bool = False
    latency_ms: float = 0
    model_version: str = "patient_qna_v1"


# ═══════════════════════════════════════════════════════════════════════════════
# Feature 4 — Case Management (from Triage)
# ═══════════════════════════════════════════════════════════════════════════════

class PatientInput(BaseModel):
    bac_si_id: str
    ho_ten: str
    tuoi: int
    gioi_tinh: str
    trieu_chung_transcript: str = ""

class DoctorApproveInput(BaseModel):
    draft_note: str = ""
    spo2: Optional[str] = None
    hr: Optional[str] = None
    bp: Optional[str] = None
    red_flags: Optional[str] = None
    uncertainty_score: Optional[float] = None

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict] = None