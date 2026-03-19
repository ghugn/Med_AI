from fastapi import APIRouter
from app.models.schemas import PatientInput, DoctorApproveInput, APIResponse, ReviewInput, NewAnswersInput
from app.services import case_service, ai_service
from app.core.logging import logger
import json

router = APIRouter(prefix="/cases", tags=["Cases"])

@router.post("/create", summary="Tạo ca bệnh mới", response_model=APIResponse)
async def create_case_endpoint(patient: PatientInput):
    logger.info(f"Khởi tạo ca mới cho bác sĩ {patient.bac_si_id}")
    result = await case_service.create_new_case(patient)
    
    return APIResponse(
        success=True,
        message="Ca bệnh đã được khởi tạo",
        data={
            "case_id": result["case_id"],
            "created_at": result["created_at"]
        }
    )

@router.post("/{case_id}/extract-and-triage", summary="Đánh giá toàn diện (FastAI)", response_model=APIResponse, tags=["AI Agents"])
async def comprehensive_triage_endpoint(case_id: str):
    logger.info(f"Bắt đầu trích xuất và đánh giá toàn diện cho case {case_id}")
    triage_result = await ai_service.process_triage(case_id)
    
    return APIResponse(
        success=triage_result.get("success", False),
        message=triage_result.get("message", "Processing completed"),
        data=triage_result.get("data")
    )

@router.post("/{case_id}/review", summary="Bác sĩ review & check rủi ro", response_model=APIResponse, tags=["AI Agents"])
async def review_case_endpoint(case_id: str, payload: ReviewInput):
    logger.info(f"Bắt đầu review cho case {case_id}")
    vitals_str = json.dumps(payload.vitals_input, ensure_ascii=False) if payload.vitals_input else "{}"
    
    review_result = await ai_service.review_case_summary(
        case_id=case_id,
        doctor_draft_note=payload.doctor_draft_note,
        vitals_input=vitals_str
    )
    
    return APIResponse(
        success=review_result.get("success", True),
        message=review_result.get("message", "Review hoàn tất"),
        data=review_result.get("data")
    )

@router.post("/{case_id}/evaluate-workflow", summary="Đánh giá luồng tiếp theo (Decision)", response_model=APIResponse, tags=["AI Agents"])
async def evaluate_workflow_endpoint(case_id: str):
    logger.info(f"Đánh giá workflow (Decision) cho case {case_id}")
    decision_result = await ai_service.evaluate_case_workflow(case_id)
    
    return APIResponse(
        success=decision_result.get("success", True),
        message=decision_result.get("message", "Đã đánh giá luồng"),
        data=decision_result.get("data")
    )

@router.post("/{case_id}/answers", summary="Nộp câu trả lời cho AI (Bước 1.b)", response_model=APIResponse, tags=["AI Agents"])
async def submit_answers_endpoint(case_id: str, payload: NewAnswersInput):
    logger.info(f"Nhận câu trả lời bổ sung cho case {case_id}")
    
    # Convert payload to dict list
    answers_list = [{"question_id": a.question_id, "answer": a.answer} for a in payload.answers]
    
    answer_result = await ai_service.process_answers(case_id, answers_list)
    
    return APIResponse(
        success=answer_result.get("success", True),
        message=answer_result.get("message", "Đã cập nhật câu trả lời"),
        data=answer_result.get("data")
    )

@router.post("/{case_id}/doctor-approve", summary="Bác sĩ phê duyệt", response_model=APIResponse)
async def doctor_approve_endpoint(case_id: str, payload: DoctorApproveInput):
    logger.info(f"Bác sĩ phê duyệt cho case {case_id}")
    await case_service.approve_case(case_id, payload)
    
    return APIResponse(
        success=True,
        message="Đã lưu hồ sơ bệnh án thành công vào Excel",
        data={"case_id": case_id}
    )
