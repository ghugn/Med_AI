from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class PatientInput(BaseModel):
    ho_ten: str = Field(..., description="Họ và tên bệnh nhân")
    tuoi: int = Field(..., description="Tuổi bệnh nhân")
    gioi_tinh: str = Field(..., description="Giới tính")
    bac_si_id: str = Field(..., description="ID của bác sĩ tiếp nhận")
    trieu_chung_transcript: str = Field(..., description="Đoạn text triệu chứng")

class ClinicalState(BaseModel):
    entities: dict = Field(default_factory=dict, description="Các thông tin bệnh lý đã trích xuất")
    missing_info: List[str] = Field(default_factory=list, description="Thông tin còn thiếu")
    problem_list: List[str] = Field(default_factory=list, description="Danh sách vấn đề")
    draft_note: str = ""
    uncertainty_score: float = 0.0

class GateDecision(BaseModel):
    alert_level: str = Field(..., description="NORMAL, WARNING, CRITICAL")
    action_required: str = Field(..., description="PROCEED, NEED_INPUT, NEED_REVIEW, STOP")
    rationale: str = Field(..., description="Lý do cho quyết định này")
    next_step: Optional[str] = None

class QuestionItem(BaseModel):
    id: str
    priority: str = Field(..., description="HIGH, MEDIUM, LOW")
    question: str
    reason: str

class AnswerItem(BaseModel):
    question_id: str
    answer: str

class AIResponseData(BaseModel):
    state: ClinicalState
    decision: GateDecision
    questions: List[QuestionItem] = Field(default_factory=list)
    extras: dict = Field(default_factory=dict)

class APIResponse(BaseModel):
    # This acts as a generic wrapper for UI
    success: bool
    message: str
    data: Optional[Any] = None

class DoctorApproveInput(BaseModel):
    draft_note: str
    spo2: Optional[str] = None
    hr: Optional[str] = None
    bp: Optional[str] = None

class ReviewInput(BaseModel):
    doctor_draft_note: str = ""
    vitals_input: Optional[dict] = None

class NewAnswersInput(BaseModel):
    answers: List[AnswerItem]

class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'ai'")
    content: str

class ChatRequest(BaseModel):
    case_id: Optional[str] = None
    user_role: str = Field(..., description="'doctor' or 'patient'")
    message: str
    history: List[ChatMessage] = Field(default_factory=list)

class ChatResponse(BaseModel):
    reply: str
