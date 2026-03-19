import uuid
import time
from datetime import datetime
from app.models.schemas import PatientInput, DoctorApproveInput
from app.db import excel_db

async def create_new_case(patient: PatientInput) -> dict:
    case_id = "CASE_" + str(uuid.uuid4())[:8].upper()
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
    await excel_db.save_case(db_record)
    
    return {
        "case_id": case_id,
        "created_at": current_time
    }

async def approve_case(case_id: str, payload: DoctorApproveInput) -> dict:
    start_time = time.time()
    update_data = {
        "Draft_Note": payload.draft_note,
        "Safety_Status": "approved_by_doctor",
        "SpO2_Final": payload.spo2,
        "HR_Final": payload.hr,
        "BP_Final": payload.bp
    }
    await excel_db.update_case(case_id, update_data)
    await excel_db.log_ai_interaction(case_id, "/cases/doctor-approve", round(float(time.time() - start_time), 2), "None", "Approved")
    
    return {"case_id": case_id}
