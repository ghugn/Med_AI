from fastapi import APIRouter
import time
import uuid
import logging
from datetime import datetime

import app.db as db
from app.schemas import PatientInput, DoctorApproveInput, APIResponse

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Cases"], prefix="/api/v1/cases")

@router.post("/create", summary="Tạo ca bệnh mới", response_model=APIResponse)
async def create_case_endpoint(patient: PatientInput):
    logger.info(f"Khởi tạo ca mới cho bác sĩ {patient.bac_si_id}")

    new_id = str(uuid.uuid4()).split("-")[0]
    case_id = f"CASE_{new_id.upper()}"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    db_record = {
        "Case_ID": case_id,
        "Ngày_giờ_khám": current_time,
        "Bác_sĩ_ID": patient.bac_si_id,
        "Họ_tên_BN": patient.ho_ten,
        "Tuổi": patient.tuoi,
        "Giới_tính": patient.gioi_tinh,
        "Triệu_chứng_Transcript": patient.trieu_chung_transcript,
        "Safety_Status": "created"
    }
    await db.save_case(db_record)

    return APIResponse(
        success=True,
        message="Ca bệnh đã được khởi tạo",
        data={"case_id": case_id, "created_at": current_time}
    )

@router.post("/{case_id}/doctor-approve", summary="Bác sĩ phê duyệt", response_model=APIResponse)
async def doctor_approve_endpoint(case_id: str, payload: DoctorApproveInput):
    logger.info(f"Bác sĩ phê duyệt cho case {case_id}")

    start_time = time.time()
    update_data = {
        "Draft_Note": payload.draft_note,
        "Safety_Status": "approved_by_doctor",
        "SpO2_Final": payload.spo2,
        "HR_Final": payload.hr,
        "BP_Final": payload.bp,
        "Red_Flag": payload.red_flags,
        "Uncertainty_Score": payload.uncertainty_score,
    }
    await db.update_case(case_id, update_data)
    await db.log_ai_interaction(case_id, "/cases/doctor-approve", round(time.time() - start_time), "None", "Approved")

    return APIResponse(
        success=True,
        message="Đã lưu hồ sơ bệnh án thành công vào Excel",
        data={"case_id": case_id}
    )
