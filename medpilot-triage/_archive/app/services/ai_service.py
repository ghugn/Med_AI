import time
from app.db import excel_db
from app.services import fastai_client
from app.core.logging import logger

async def process_triage(case_id: str) -> dict:
    """
    Trích xuất thông tin lâm sàng, đánh giá triage và câu hỏi từ transcript theo chuẩn Gate.
    Gọi AI Model → parse → validate → lưu DB → trả kết quả.
    """
    start_time = time.time()
    
    # 1. Đọc dữ liệu từ DB
    case_data = await excel_db.get_case(case_id)
    if not case_data:
        logger.error(f"Không tìm thấy case_id: {case_id}")
        return {
            "success": False,
            "message": f"Không tìm thấy ca bệnh với ID: {case_id}",
            "data": None
        }
    
    transcript = case_data.get("Triệu_chứng_Transcript", "")
    if not transcript or str(transcript).strip() == "" or str(transcript) == "nan":
        logger.warning(f"Case {case_id} không có transcript")
        return {
            "success": False,
            "message": "Không có dữ liệu transcript để kiểm tra",
            "data": None
        }
        
    # Lấy thông tin bệnh nhân đã biết từ DB
    ho_ten = case_data.get("Họ_tên_BN", "")
    tuoi = case_data.get("Tuổi", "")
    gioi_tinh = case_data.get("Giới_tính", "")
    patient_info = f"Người bệnh: {ho_ten}, {tuoi} tuổi, Giới tính: {gioi_tinh}"
    extracted_entities = str(case_data.get("Extracted_Entities", "{}"))
    
    # 2. Gọi FastAI API (placeholder) để đánh giá triage (Gate method)
    ai_response = await fastai_client.extract_and_triage(
        transcript=str(transcript), 
        patient_info=patient_info, 
        existing_structured_data_json=extracted_entities,
        case_id=case_id
    )
    
    decision = ai_response.decision
    state = ai_response.state
    
    # 3. Lưu kết quả vào DB
    update_data = {
        "Red_Flag": decision.alert_level,
        "Missing_Info": str(state.missing_info),
        "Safety_Status": decision.action_required,
        "Extracted_Entities": str(state.entities),
        "Draft_Note": state.draft_note,
        "Problem_List": str(state.problem_list),
        "Uncertainty_Score": state.uncertainty_score
    }
        
    await excel_db.update_case(case_id, update_data)
    
    # 4. Log interaction
    latency = round(float(time.time() - start_time), 2)
    await excel_db.log_ai_interaction(
        case_id, "/cases/extract-and-triage", latency, "", str(ai_response.model_dump())
    )
    
    logger.info(f"Triage hoàn tất cho case {case_id} trong {latency}s. Action: {decision.action_required}")
    
    success = decision.action_required == "PROCEED"
    message = decision.rationale if decision.rationale else "Đóng cửa (Gate) - Hãy trả lời các câu hỏi."
    if success:
         message = "Triage sơ bộ thành công, đủ điều kiện đi tiếp."

    return {
        "success": success,
        "message": message,
        "data": ai_response.model_dump()
    }

async def review_case_summary(case_id: str, doctor_draft_note: str, vitals_input: str) -> dict:
    """
    Step 3: Bác sĩ review/sửa đổi summary -> gọi AI check lại lần cuối.
    Phát hiện thiếu/mâu thuẫn, trả về checklist.
    """
    start_time = time.time()
    
    case_data = await excel_db.get_case(case_id)
    if not case_data:
        return {"success": False, "message": "Không tìm thấy case", "data": None}
        
    ho_ten = case_data.get("Họ_tên_BN", "")
    tuoi = case_data.get("Tuổi", "")
    gioi_tinh = case_data.get("Giới_tính", "")
    patient_info = f"Người bệnh: {ho_ten}, {tuoi} tuổi, Giới tính: {gioi_tinh}"
    
    # Gom lại nháp từ DB nếu có
    final_summary_json = {
        "draft_note": case_data.get("Draft_Note", ""),
        "problem_list": case_data.get("Problem_List", ""),
        "red_flag": case_data.get("Red_Flag", "Thấp"),
        "uncertainty_score": case_data.get("Uncertainty_Score", 0.0)
    }
    
    ai_response = await fastai_client.review_clinical_summary(
        case_id=case_id,
        patient_info=patient_info,
        final_summary_json=str(final_summary_json),
        doctor_draft_note=doctor_draft_note,
        vitals_input=vitals_input
    )
    
    decision = ai_response.decision
    state = ai_response.state
    
    # Lưu Safety_Status mới nhất để chặn/cho phép chốt HSBA
    update_data = {
        "Safety_Status": decision.action_required,
        "Missing_Info": str(state.missing_info) if state.missing_info else case_data.get("Missing_Info", "[]"),
        "Red_Flag": decision.alert_level,
        "Extracted_Entities": str(state.entities)
    }
    await excel_db.update_case(case_id, update_data)
    
    latency = round(float(time.time() - start_time), 2)
    await excel_db.log_ai_interaction(
        case_id, "/cases/review", latency, "", str(ai_response.model_dump())
    )
    
    success = decision.action_required == "PROCEED"
    return {
        "success": success,
        "message": decision.rationale if decision.rationale else "Đã review. Xin hoàn thành checklist xác nhận.",
        "data": ai_response.model_dump()
    }

async def evaluate_case_workflow(case_id: str) -> dict:
    """
    Step 4: Quyết định luồng (Workflow Decision) dựa trên trạng thái DB hiện tại.
    """
    start_time = time.time()
    
    case_data = await excel_db.get_case(case_id)
    if not case_data:
        return {"success": False, "message": "Không tìm thấy case", "data": None}
        
    ho_ten = case_data.get("Họ_tên_BN", "")
    tuoi = case_data.get("Tuổi", "")
    gioi_tinh = case_data.get("Giới_tính", "")
    patient_info = f"Người bệnh: {ho_ten}, {tuoi} tuổi, Giới tính: {gioi_tinh}"
    
    # Gom toàn bộ trạng thái hiện tại (state json)
    structured_state = {
        "extracted_entities": case_data.get("Extracted_Entities", "{}"),
        "draft_note": case_data.get("Draft_Note", ""),
        "missing_info": case_data.get("Missing_Info", "[]"),
        "red_flag": case_data.get("Red_Flag", "Thấp")
    }
    import json
    
    ai_response = await fastai_client.evaluate_workflow_decision(
        case_id=case_id,
        patient_info=patient_info,
        structured_state_json=json.dumps(structured_state, ensure_ascii=False)
    )
    
    decision = ai_response.decision
    
    # Cập nhật Safety_Status nếu cần
    update_data = {
        "Safety_Status": decision.action_required
    }
    
    # Cập nhật Red_Flag nếu AI thay đổi
    if decision.alert_level != "NORMAL":
        update_data["Red_Flag"] = decision.alert_level
        
    await excel_db.update_case(case_id, update_data)
    
    latency = round(float(time.time() - start_time), 2)
    await excel_db.log_ai_interaction(
        case_id, "/cases/evaluate-workflow", latency, "", str(ai_response.model_dump())
    )
    
    success = decision.action_required == "PROCEED"
    
    return {
        "success": success,
        "message": f"Quyết định: {decision.action_required} - {decision.rationale}",
        "data": ai_response.model_dump()
    }

async def process_answers(case_id: str, new_answers: list) -> dict:
    """
    Step 1.b: Nhận câu trả lời từ người dùng, merge vào DB qua FastAI.
    """
    start_time = time.time()
    
    case_data = await excel_db.get_case(case_id)
    if not case_data:
        return {"success": False, "message": "Không tìm thấy case", "data": None}
        
    import json
    # Gom state cũ
    structured_state = {
        "extracted_entities": case_data.get("Extracted_Entities", "{}"),
        "missing_info": case_data.get("Missing_Info", "[]"),
    }
    
    answers_json = json.dumps({"answers": new_answers}, ensure_ascii=False)
    
    ai_response = await fastai_client.merge_question_answers(
        case_id=case_id,
        current_structured_state_json=json.dumps(structured_state, ensure_ascii=False),
        new_answers_json=answers_json
    )
    decision = ai_response.decision
    state = ai_response.state
    
    update_data = {
        "Missing_Info": str(state.missing_info),
        "Extracted_Entities": str(state.entities),
        "Safety_Status": decision.action_required
    }
        
    await excel_db.update_case(case_id, update_data)
    
    latency = round(float(time.time() - start_time), 2)
    await excel_db.log_ai_interaction(
        case_id, "/cases/answers", latency, "", str(ai_response.model_dump())
    )
    
    success = decision.action_required == "PROCEED"
    return {
        "success": success,
        "message": f"Đã ghi nhận trả lời. Hành động tiếp theo: {decision.action_required}",
        "data": ai_response.model_dump()
    }

async def process_chat(payload) -> dict: # payload is ChatRequest but avoid tight coupling here if possible, or import and type it
    """
    Xử lý logic chat giữa người dùng (Bác sĩ/Bệnh nhân) và AI.
    - Chuyển tiếp câu hỏi và lịch sử cho FastAI Client.
    - Ghi log (không block event loop).
    """
    start_time = time.time()
    
    # 1. Gọi FastAI API thông qua fastai_client
    reply_text = await fastai_client.chat_interaction(
        user_role=payload.user_role,
        message=payload.message,
        history=[h.model_dump() for h in payload.history]
    )
    
    # 2. Ghi log tương tác
    latency = round(float(time.time() - start_time), 2)
    case_id_tag = payload.case_id if payload.case_id else "NoCase"
    await excel_db.log_ai_interaction(
        case_id_tag, 
        "/chat", 
        latency, 
        "", 
        f"Role: {payload.user_role} | Message: {payload.message} | Reply: {reply_text}"
    )
    
    # 3. Trả về kết quả
    return {
        "reply": reply_text
    }
