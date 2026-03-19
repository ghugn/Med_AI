"""
AI Prompts & vLLM Client — MedPilot PoC
Gộp: vLLM HTTP client + tất cả prompt templates + các hàm gọi AI.
"""
import os
import httpx
import json
import logging
from typing import List, Dict, Optional
from schemas import ClinicalState, GateDecision, QuestionItem, AIResponseData

logger = logging.getLogger("medpilot")

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG (đọc từ .env, fallback mặc định)
# ═══════════════════════════════════════════════════════════════════════════════

VLLM_BASE_URL = os.getenv("VLLM_BASE_URL", "http://localhost:8001/v1")
VLLM_MODEL_NAME = os.getenv("VLLM_MODEL_NAME", "default")
VLLM_TIMEOUT = float(os.getenv("VLLM_TIMEOUT", "180"))


# ═══════════════════════════════════════════════════════════════════════════════
# vLLM CLIENT
# ═══════════════════════════════════════════════════════════════════════════════

async def chat_completion(
    messages: List[Dict[str, str]],
    max_tokens: int = 1024,
    temperature: float = 0.3,
    timeout: float = None,
) -> str:
    """Gọi vLLM /v1/chat/completions và trả về text trả lời."""
    url = f"{VLLM_BASE_URL}/chat/completions"
    payload = {
        "model": VLLM_MODEL_NAME,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
    }
    _timeout = timeout if timeout is not None else VLLM_TIMEOUT

    logger.info(f"[vLLM] POST {url} | model={VLLM_MODEL_NAME} | msgs={len(messages)}")

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=_timeout)

    if response.status_code != 200:
        logger.error(f"[vLLM] HTTP {response.status_code}: {response.text[:300]}")
        raise httpx.HTTPStatusError(
            f"vLLM trả về lỗi {response.status_code}",
            request=response.request,
            response=response,
        )

    data = response.json()
    try:
        text = data["choices"][0]["message"]["content"]
        logger.info(f"[vLLM] OK — {len(text)} chars")
        return text
    except (KeyError, IndexError) as e:
        logger.error(f"[vLLM] Parse lỗi: {e} | raw: {str(data)[:300]}")
        raise ValueError(f"Không thể parse response từ vLLM: {e}")


async def chat_completion_safe(
    messages: List[Dict[str, str]],
    fallback: str = "Xin lỗi, hệ thống AI hiện không khả dụng. Vui lòng thử lại sau.",
    max_tokens: int = 1024,
    temperature: float = 0.3,
    timeout: float = None,
) -> str:
    """Gọi chat_completion, trả về `fallback` nếu có lỗi (không raise exception)."""
    try:
        return await chat_completion(messages, max_tokens, temperature, timeout)
    except Exception as e:
        logger.warning(f"[vLLM] Lỗi kết nối/parse, dùng fallback. Chi tiết: {e}")
        return fallback


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT TEMPLATES
# ═══════════════════════════════════════════════════════════════════════════════

COMPREHENSIVE_PROMPT_TEMPLATE = """NGUYÊN TẮC
- Không bịa. Không kê đơn/khuyến cáo điều trị cụ thể.
- Nếu thiếu dữ liệu quan trọng => decision: "NEED_INPUT", không được "kết luận".
- Output chỉ là JSON hợp lệ, không markdown, không giải thích ngoài JSON.
ĐẦU VÀO
case_id: {case_id}
patient_info: {patient_info}
clinical_state_json:
{extracted_json}
(optional) raw_transcript:
{transcript}
KIỂM TRA ĐỦ DỮ LIỆU (GATE)
- Nếu có dấu hiệu nặng (đau ngực, khó thở, ngất, rối loạn ý thức, yếu liệt, co giật, xuất huyết nhiều, v.v.)
  và thiếu ít nhất 1 trong: spo2/hr/bp => coi là CHƯA ĐỦ.
- Nếu timeline mơ hồ (khởi phát/diễn tiến không rõ) => CHƯA ĐỦ.
- Nếu mâu thuẫn dữ liệu (tuổi/giới/tên/vitals mâu thuẫn) => CHƯA ĐỦ.
YÊU CẦU OUTPUT
A) Nếu CHƯA ĐỦ => trả:
- decision: alert_level="WARNING", action_required="NEED_INPUT", rationale="...", next_step="Yêu cầu đo sinh hiệu"
- state: update missing_info
- questions: tối đa 8 câu hỏi (ưu tiên HIGH)
B) Nếu ĐỦ => trả:
- decision: alert_level="NORMAL", action_required="PROCEED", rationale="...", next_step="Review lại state"
- state: update draft_note, problem_list, uncertainty_score, entities
- questions: []
ĐỊNH DẠNG OUTPUT (bắt buộc, chỉ JSON thuần):
{{
  "state": {{
    "entities": {{}},
    "missing_info": [],
    "problem_list": [],
    "draft_note": "",
    "uncertainty_score": 0.0
  }},
  "decision": {{
    "alert_level": "NORMAL",
    "action_required": "PROCEED",
    "rationale": "",
    "next_step": null
  }},
  "questions": [
    {{ "id": "Q1", "priority": "HIGH", "question": "", "reason": "" }}
  ]
}}"""

DOCTOR_REVIEW_PROMPT_TEMPLATE = """Mục tiêu: phát hiện thiếu dữ liệu, mâu thuẫn, điểm cần xác nhận; đề xuất checklist xác nhận ngắn gọn.
Không kê đơn/khuyến cáo điều trị. Không đưa chẩn đoán chắc chắn nếu dữ liệu thiếu.
NGUYÊN TẮC
- Chỉ dựa trên dữ liệu đầu vào. Không bịa.
- Output chỉ JSON hợp lệ, không markdown, không giải thích ngoài JSON.
ĐẦU VÀO
case_id: {case_id}
patient_info: {patient_info}
clinical_state_json:
{final_summary_json}
doctor_draft_note: {doctor_draft_note}
vitals_input: {vitals_input}
ĐỊNH DẠNG OUTPUT (bắt buộc):
{{
  "state": {{
    "entities": {{}},
    "missing_info": [],
    "problem_list": [],
    "draft_note": "",
    "uncertainty_score": 0.0
  }},
  "decision": {{
    "alert_level": "NORMAL",
    "action_required": "PROCEED",
    "rationale": "",
    "next_step": null
  }},
  "extras": {{
    "conflicts": [],
    "doctor_confirmation_checklist": [
      {{ "id": "C1", "item": "", "priority": "HIGH" }}
    ]
  }}
}}"""

WORKFLOW_DECISION_PROMPT_TEMPLATE = """Mục tiêu: dựa trên dữ liệu hiện có để quyết định bước tiếp theo.
NGUYÊN TẮC: Không bịa. Output chỉ JSON hợp lệ.
ĐẦU VÀO
case_id: {case_id}
patient_info: {patient_info}
clinical_state_json:
{structured_state_json}
QUY TẮC RA QUYẾT ĐỊNH:
- Dấu hiệu nguy cấp (đau ngực, SpO2 thấp, ...) => alert_level="CRITICAL", action_required="NEED_REVIEW"
- Thiếu vitals quan trọng hoặc timeline mơ hồ => alert_level="WARNING", action_required="NEED_INPUT"
- Đủ dữ liệu, không nguy cấp => alert_level="NORMAL", action_required="PROCEED"
ĐỊNH DẠNG OUTPUT (bắt buộc):
{{
  "decision": {{
    "alert_level": "NORMAL",
    "action_required": "PROCEED",
    "rationale": "Lý do ra quyết định này",
    "next_step": null
  }},
  "state": {{
    "entities": {{}},
    "missing_info": [],
    "problem_list": [],
    "draft_note": "",
    "uncertainty_score": 0.0
  }},
  "extras": {{
    "evidence": []
  }}
}}"""

MERGE_ANSWERS_PROMPT_TEMPLATE = """Mục tiêu: hợp nhất câu trả lời mới vào clinical state, cập nhật missing_info và quyết định bước tiếp theo.
NGUYÊN TẮC: Không bịa. Output chỉ JSON hợp lệ.
ĐẦU VÀO
case_id: {case_id}
current_clinical_state_json:
{current_structured_state_json}
new_answers_json:
{new_answers_json}
ĐỊNH DẠNG OUTPUT (bắt buộc):
{{
  "state": {{
    "entities": {{}},
    "missing_info": [],
    "problem_list": [],
    "draft_note": "",
    "uncertainty_score": 0.0
  }},
  "decision": {{
    "alert_level": "NORMAL",
    "action_required": "PROCEED",
    "rationale": "",
    "next_step": null
  }},
  "questions": [],
  "extras": {{
    "conflicts": []
  }}
}}"""

DOCTOR_CHAT_PROMPT = """Bạn là trợ lý AI chuyên môn y khoa (MedPilot Assistant). Người dùng là BÁC SĨ.
Trả lời ngắn gọn, súc tích, chuyên môn. Không giải thích khái niệm cơ bản trừ khi được yêu cầu.

Lịch sử hội thoại:
{history}

Câu hỏi mới từ bác sĩ: {message}

Trả lời:"""

PATIENT_CHAT_PROMPT = """Bạn là trợ lý y tế ảo (MedPilot Triage Bot). Người dùng là BỆNH NHÂN.
Trả lời bằng ngôn ngữ dễ hiểu, thân thiện. TUYỆT ĐỐI:
1. KHÔNG tự ý chẩn đoán xác định bệnh.
2. KHÔNG kê đơn thuốc hoặc tư vấn liều lượng cụ thể.
3. Luôn khuyên bệnh nhân đến cơ sở y tế nếu có dấu hiệu nặng.
4. Chỉ cung cấp kiến thức giáo dục sức khỏe chung.

Lịch sử hội thoại:
{history}

Câu hỏi mới từ bệnh nhân: {message}

Trả lời:"""


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _parse_json_response(raw: str) -> dict:
    """Parse JSON từ response của LLM (có thể có markdown code fence)."""
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        text = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


# ═══════════════════════════════════════════════════════════════════════════════
# AI FUNCTIONS (Gate Triage, Review, Workflow, Merge, Chat)
# ═══════════════════════════════════════════════════════════════════════════════

async def extract_and_triage(
    transcript: str,
    patient_info: str = "",
    existing_structured_data_json: str = "",
    case_id: str = ""
) -> AIResponseData:
    """Trích xuất thông tin lâm sàng và đánh giá triage."""
    logger.info(f"[AI] extract_and_triage — case {case_id}")
    prompt = COMPREHENSIVE_PROMPT_TEMPLATE.format(
        case_id=case_id,
        patient_info=patient_info,
        extracted_json=existing_structured_data_json,
        transcript=transcript,
    )
    messages = [
        {"role": "system", "content": "Bạn là AI y tế phân tích dữ liệu lâm sàng. Chỉ trả về JSON hợp lệ."},
        {"role": "user", "content": prompt},
    ]
    raw = await chat_completion_safe(messages=messages, max_tokens=2048, temperature=0.1)
    try:
        data = _parse_json_response(raw)
        return AIResponseData(**data)
    except Exception as e:
        logger.warning(f"[AI] Parse lỗi triage response: {e}. Dùng fallback mock.")
        return _mock_triage_fallback(existing_structured_data_json)


def _mock_triage_fallback(existing_json: str) -> AIResponseData:
    is_enough = "spo2" in existing_json.lower()
    if is_enough:
        return AIResponseData(
            state=ClinicalState(
                entities={"vitals": {"spo2": "98%"}},
                missing_info=[],
                problem_list=["Triệu chứng chưa xác định rõ"],
                draft_note="Bệnh nhân có triệu chứng cần theo dõi. Sinh hiệu trong giới hạn an toàn tạm thời.",
                uncertainty_score=0.2,
            ),
            decision=GateDecision(
                alert_level="NORMAL",
                action_required="PROCEED",
                rationale="Đã có đủ thông tin sinh hiệu nền tảng để đánh giá triệu chứng.",
            ),
            questions=[]
        )
    return AIResponseData(
        state=ClinicalState(
            entities={},
            missing_info=["SpO2", "Nhịp đập (HR)", "Huyết áp (BP)"],
            problem_list=[],
            draft_note="",
            uncertainty_score=0.9
        ),
        decision=GateDecision(
             alert_level="WARNING",
             action_required="NEED_INPUT",
             rationale="Thiếu thông tin sinh hiệu quan trọng để đánh giá triệu chứng từ transcript.",
        ),
        questions=[
            QuestionItem(id="Q1", priority="HIGH", question="Xin hỏi chỉ số SpO2 của bệnh nhân là bao nhiêu?", reason="Xác định tình trạng hô hấp."),
            QuestionItem(id="Q2", priority="MEDIUM", question="Triệu chứng này bắt đầu từ bao giờ?", reason="Khảo sát timeline."),
        ]
    )


async def review_clinical_summary(
    case_id: str,
    patient_info: str,
    final_summary_json: str,
    doctor_draft_note: str = "",
    vitals_input: str = "{}",
) -> AIResponseData:
    """Review bản tóm tắt lâm sàng, tìm gaps và tạo checklist xác nhận."""
    logger.info(f"[AI] review_clinical_summary — case {case_id}")
    prompt = DOCTOR_REVIEW_PROMPT_TEMPLATE.format(
        case_id=case_id,
        patient_info=patient_info,
        final_summary_json=final_summary_json,
        doctor_draft_note=doctor_draft_note,
        vitals_input=vitals_input,
    )
    messages = [
        {"role": "system", "content": "Bạn là AI y tế review hồ sơ. Chỉ trả về JSON hợp lệ."},
        {"role": "user", "content": prompt},
    ]
    raw = await chat_completion_safe(messages=messages, max_tokens=1024, temperature=0.1)
    try:
        data = _parse_json_response(raw)
        return AIResponseData(**data)
    except Exception as e:
        logger.warning(f"[AI] Parse lỗi review response: {e}. Dùng fallback mock.")
        return AIResponseData(
            state=ClinicalState(
                entities={},
                missing_info=["Thiếu thông tin SpO2"],
                problem_list=[],
                draft_note="Bệnh nhân có triệu chứng hô hấp nhưng chưa đo SpO2.",
                uncertainty_score=0.8
            ),
            decision=GateDecision(
                alert_level="WARNING",
                action_required="NEED_REVIEW",
                rationale="Cần bác sĩ xác nhận lại chỉ số sống còn."
            ),
            questions=[],
            extras={
                 "doctor_confirmation_checklist": [
                    {"id": "C1", "item": "Xác nhận rằng bệnh nhân không có tiền sử hen suyễn?", "priority": "HIGH"},
                    {"id": "C2", "item": "Xác nhận chỉ số SpO2 hiện tại > 95%?", "priority": "HIGH"}
                 ]
            }
        )


async def evaluate_workflow_decision(
    case_id: str,
    patient_info: str,
    structured_state_json: str,
) -> AIResponseData:
    """Đánh giá bước tiếp theo của workflow."""
    logger.info(f"[AI] evaluate_workflow_decision — case {case_id}")
    prompt = WORKFLOW_DECISION_PROMPT_TEMPLATE.format(
        case_id=case_id,
        patient_info=patient_info,
        structured_state_json=structured_state_json,
    )
    messages = [
        {"role": "system", "content": "Bạn là AI y tế ra quyết định workflow. Chỉ trả về JSON hợp lệ."},
        {"role": "user", "content": prompt},
    ]
    raw = await chat_completion_safe(messages=messages, max_tokens=512, temperature=0.1)
    try:
        data = _parse_json_response(raw)
        return AIResponseData(**data)
    except Exception as e:
        logger.warning(f"[AI] Parse lỗi workflow response: {e}. Dùng fallback mock.")
        if "spo2" not in structured_state_json.lower():
             return AIResponseData(
                state=ClinicalState(
                    entities={},
                    missing_info=["SpO2", "Nhịp tim"],
                    problem_list=[],
                    draft_note="Thiếu thông tin sinh hiệu",
                    uncertainty_score=0.9
                ),
                decision=GateDecision(
                    alert_level="WARNING",
                    action_required="NEED_INPUT",
                    rationale="Thiếu thông tin sinh hiệu cơ bản (SpO2)."
                ),
                questions=[]
             )
        return AIResponseData(
            state=ClinicalState(
                entities={"vitals":{"spo2":"ok"}},
                missing_info=[],
                problem_list=[],
                draft_note="Đủ dữ liệu",
                uncertainty_score=0.1
            ),
            decision=GateDecision(
                alert_level="NORMAL",
                action_required="PROCEED",
                rationale="Đã có đủ thông tin lâm sàng và sinh hiệu để đưa ra kết luận sơ bộ.",
            ),
            questions=[]
        )


async def merge_question_answers(
    case_id: str,
    current_structured_state_json: str,
    new_answers_json: str,
) -> AIResponseData:
    """Hợp nhất câu trả lời mới vào structured state."""
    logger.info(f"[AI] merge_question_answers — case {case_id}")
    prompt = MERGE_ANSWERS_PROMPT_TEMPLATE.format(
        case_id=case_id,
        current_structured_state_json=current_structured_state_json,
        new_answers_json=new_answers_json,
    )
    messages = [
        {"role": "system", "content": "Bạn là AI y tế hợp nhất dữ liệu. Chỉ trả về JSON hợp lệ."},
        {"role": "user", "content": prompt},
    ]
    raw = await chat_completion_safe(messages=messages, max_tokens=1024, temperature=0.1)
    try:
        data = _parse_json_response(raw)
        return AIResponseData(**data)
    except Exception as e:
        logger.warning(f"[AI] Parse lỗi merge response: {e}. Dùng fallback mock.")
        is_enough = "spo2" in new_answers_json.lower()
        return AIResponseData(
            state=ClinicalState(
                 entities={"vitals": {"spo2": "95%"}} if is_enough else {},
                 missing_info=[] if is_enough else ["SpO2"],
                 problem_list=[],
                 draft_note="",
                 uncertainty_score=0.1 if is_enough else 0.8
            ),
            decision=GateDecision(
                 alert_level="NORMAL" if is_enough else "WARNING",
                 action_required="PROCEED" if is_enough else "NEED_INPUT",
                 rationale="OK" if is_enough else "Thiếu SpO2"
            ),
            questions=(
                 [] if is_enough else [QuestionItem(id="Q_next_1", priority="HIGH", question="Vui lòng đo ngay SpO2 cho bệnh nhân?", reason="Loại trừ suy hô hấp")]
            )
        )


async def chat_interaction(user_role: str, message: str, history: list) -> str:
    """Gọi vLLM để chat theo role (doctor/patient). Fallback mock nếu lỗi."""
    logger.info(f"[AI] chat_interaction — role={user_role}")
    history_str = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in history])
    template = DOCTOR_CHAT_PROMPT if user_role == "doctor" else PATIENT_CHAT_PROMPT
    prompt = template.format(message=message, history=history_str)
    messages = [{"role": "user", "content": prompt}]
    fallback = (
        "Theo guideline hiện hành, với bệnh nhân có triệu chứng này cần ưu tiên thăm khám chuyên khoa ngay."
        if user_role == "doctor"
        else "Để an toàn nhất, bạn nên đến cơ sở y tế gần nhất để bác sĩ thăm khám và có chỉ định cụ thể."
    )
    return await chat_completion_safe(
        messages=messages,
        fallback=fallback,
        max_tokens=512,
        temperature=0.7,
    )
