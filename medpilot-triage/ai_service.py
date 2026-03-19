"""
AI Service — MedPilot PoC
Business logic: triage, review, workflow, answers, chat.
"""
import time
import json
import logging
import db
import ai_prompts

logger = logging.getLogger("medpilot")


async def process_triage(case_id: str) -> dict:
    """Trích xuất thông tin lâm sàng, đánh giá triage và câu hỏi từ transcript."""
    start_time = time.time()
    case_data = await db.get_case(case_id)
    if not case_data:
        logger.error(f"Không tìm thấy case_id: {case_id}")
        return {"success": False, "message": f"Không tìm thấy ca bệnh với ID: {case_id}", "data": None}

    transcript = case_data.get("Triệu_chứng_Transcript", "")
    if not transcript or str(transcript).strip() == "" or str(transcript) == "nan":
        logger.warning(f"Case {case_id} không có transcript")
        return {"success": False, "message": "Không có dữ liệu transcript để kiểm tra", "data": None}

    ho_ten = case_data.get("Họ_tên_BN", "")
    tuoi = case_data.get("Tuổi", "")
    gioi_tinh = case_data.get("Giới_tính", "")
    patient_info = f"Người bệnh: {ho_ten}, {tuoi} tuổi, Giới tính: {gioi_tinh}"
    extracted_entities = str(case_data.get("Extracted_Entities", "{}"))

    ai_response = await ai_prompts.extract_and_triage(
        transcript=str(transcript),
        patient_info=patient_info,
        existing_structured_data_json=extracted_entities,
        case_id=case_id
    )

    decision = ai_response.decision
    state = ai_response.state

    update_data = {
        "Red_Flag": decision.alert_level,
        "Missing_Info": str(state.missing_info),
        "Safety_Status": decision.action_required,
        "Extracted_Entities": str(state.entities),
        "Draft_Note": state.draft_note,
        "Problem_List": str(state.problem_list),
        "Uncertainty_Score": state.uncertainty_score
    }
    await db.update_case(case_id, update_data)

    latency = round(float(time.time() - start_time), 2)
    await db.log_ai_interaction(case_id, "/cases/extract-and-triage", latency, "", str(ai_response.model_dump()))

    logger.info(f"Triage hoàn tất cho case {case_id} trong {latency}s. Action: {decision.action_required}")

    success = decision.action_required == "PROCEED"
    message = decision.rationale if decision.rationale else "Đóng cửa (Gate) - Hãy trả lời các câu hỏi."
    if success:
         message = "Triage sơ bộ thành công, đủ điều kiện đi tiếp."

    return {"success": success, "message": message, "data": ai_response.model_dump()}


async def review_case_summary(case_id: str, doctor_draft_note: str, vitals_input: str) -> dict:
    """Bác sĩ review/sửa đổi summary -> gọi AI check lại lần cuối."""
    start_time = time.time()
    case_data = await db.get_case(case_id)
    if not case_data:
        return {"success": False, "message": "Không tìm thấy case", "data": None}

    ho_ten = case_data.get("Họ_tên_BN", "")
    tuoi = case_data.get("Tuổi", "")
    gioi_tinh = case_data.get("Giới_tính", "")
    patient_info = f"Người bệnh: {ho_ten}, {tuoi} tuổi, Giới tính: {gioi_tinh}"

    final_summary_json = {
        "draft_note": case_data.get("Draft_Note", ""),
        "problem_list": case_data.get("Problem_List", ""),
        "red_flag": case_data.get("Red_Flag", "Thấp"),
        "uncertainty_score": case_data.get("Uncertainty_Score", 0.0)
    }

    ai_response = await ai_prompts.review_clinical_summary(
        case_id=case_id,
        patient_info=patient_info,
        final_summary_json=str(final_summary_json),
        doctor_draft_note=doctor_draft_note,
        vitals_input=vitals_input
    )

    decision = ai_response.decision
    state = ai_response.state

    update_data = {
        "Safety_Status": decision.action_required,
        "Missing_Info": str(state.missing_info) if state.missing_info else case_data.get("Missing_Info", "[]"),
        "Red_Flag": decision.alert_level,
        "Extracted_Entities": str(state.entities)
    }
    await db.update_case(case_id, update_data)

    latency = round(float(time.time() - start_time), 2)
    await db.log_ai_interaction(case_id, "/cases/review", latency, "", str(ai_response.model_dump()))

    success = decision.action_required == "PROCEED"
    return {
        "success": success,
        "message": decision.rationale if decision.rationale else "Đã review. Xin hoàn thành checklist xác nhận.",
        "data": ai_response.model_dump()
    }


async def evaluate_case_workflow(case_id: str) -> dict:
    """Quyết định luồng (Workflow Decision) dựa trên trạng thái DB hiện tại."""
    start_time = time.time()
    case_data = await db.get_case(case_id)
    if not case_data:
        return {"success": False, "message": "Không tìm thấy case", "data": None}

    ho_ten = case_data.get("Họ_tên_BN", "")
    tuoi = case_data.get("Tuổi", "")
    gioi_tinh = case_data.get("Giới_tính", "")
    patient_info = f"Người bệnh: {ho_ten}, {tuoi} tuổi, Giới tính: {gioi_tinh}"

    structured_state = {
        "extracted_entities": case_data.get("Extracted_Entities", "{}"),
        "draft_note": case_data.get("Draft_Note", ""),
        "missing_info": case_data.get("Missing_Info", "[]"),
        "red_flag": case_data.get("Red_Flag", "Thấp")
    }

    ai_response = await ai_prompts.evaluate_workflow_decision(
        case_id=case_id,
        patient_info=patient_info,
        structured_state_json=json.dumps(structured_state, ensure_ascii=False)
    )

    decision = ai_response.decision

    update_data = {"Safety_Status": decision.action_required}
    if decision.alert_level != "NORMAL":
        update_data["Red_Flag"] = decision.alert_level
    await db.update_case(case_id, update_data)

    latency = round(float(time.time() - start_time), 2)
    await db.log_ai_interaction(case_id, "/cases/evaluate-workflow", latency, "", str(ai_response.model_dump()))

    success = decision.action_required == "PROCEED"
    return {
        "success": success,
        "message": f"Quyết định: {decision.action_required} - {decision.rationale}",
        "data": ai_response.model_dump()
    }


async def process_answers(case_id: str, new_answers: list) -> dict:
    """Nhận câu trả lời từ người dùng, merge vào DB qua AI."""
    start_time = time.time()
    case_data = await db.get_case(case_id)
    if not case_data:
        return {"success": False, "message": "Không tìm thấy case", "data": None}

    structured_state = {
        "extracted_entities": case_data.get("Extracted_Entities", "{}"),
        "missing_info": case_data.get("Missing_Info", "[]"),
    }
    answers_json = json.dumps({"answers": new_answers}, ensure_ascii=False)

    ai_response = await ai_prompts.merge_question_answers(
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
    await db.update_case(case_id, update_data)

    latency = round(float(time.time() - start_time), 2)
    await db.log_ai_interaction(case_id, "/cases/answers", latency, "", str(ai_response.model_dump()))

    success = decision.action_required == "PROCEED"
    return {
        "success": success,
        "message": f"Đã ghi nhận trả lời. Hành động tiếp theo: {decision.action_required}",
        "data": ai_response.model_dump()
    }


async def process_chat(payload) -> dict:
    """Xử lý logic chat giữa người dùng (Bác sĩ/Bệnh nhân) và AI."""
    start_time = time.time()

    reply_text = await ai_prompts.chat_interaction(
        user_role=payload.user_role,
        message=payload.message,
        history=[h.model_dump() for h in payload.history]
    )

    latency = round(float(time.time() - start_time), 2)
    case_id_tag = payload.case_id if payload.case_id else "NoCase"
    await db.log_ai_interaction(
        case_id_tag,
        "/chat",
        latency,
        "",
        f"Role: {payload.user_role} | Message: {payload.message} | Reply: {reply_text}"
    )

    return {"reply": reply_text}
