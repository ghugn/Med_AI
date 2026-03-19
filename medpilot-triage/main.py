"""
MedPilot API — PoC Entry Point
Gộp: FastAPI app, config, CORS, logging, exception handlers, lifespan, static serving, và tất cả API routes.
Chạy: python main.py
"""
import os
import sys

# Load .env trước tất cả
from dotenv import load_dotenv
load_dotenv()

import json
import uuid
import time
import asyncio
import logging
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from schemas import (
    PatientInput, DoctorApproveInput, APIResponse, ReviewInput,
    NewAnswersInput, ChatRequest, ChatResponse,
    RAGQueryRequest, RAGQueryResponse,
)
import db
import ai_service
import rag_service
import medpilot_bridge


# ═══════════════════════════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logging.getLogger("uvicorn").setLevel(logging.INFO)
logging.getLogger("fastapi").setLevel(logging.INFO)
logger = logging.getLogger("medpilot")


# ═══════════════════════════════════════════════════════════════════════════════
# LIFESPAN (startup / shutdown)
# ═══════════════════════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting MedPilot API (PoC)...")

    # Khởi tạo Excel DB
    db.init_db()

    # Khởi tạo RAG (async, chạy trong thread riêng)
    logger.info("[RAG] Bắt đầu khởi tạo RAG service...")
    loop = asyncio.get_running_loop()
    success = await loop.run_in_executor(None, rag_service.initialize)
    if success:
        logger.info("[RAG] ✅ RAG service sẵn sàng")
    else:
        logger.warning(
            "[RAG] ⚠️ RAG service khởi tạo không thành công "
            "(có thể thiếu package hoặc Excel folder trống). "
            "Backend vẫn hoạt động bình thường."
        )

    yield

    logger.info("API shutdown an toàn.")


# ═══════════════════════════════════════════════════════════════════════════════
# APP FACTORY
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="MedPilot API (Demo POC)",
    description="Backend trung chuyển cho trợ lý AI y khoa MedPilot. Tích hợp Safety Layer & Logging.",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# ─── CORS ─────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Exception Handlers ──────────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    resp = APIResponse(
        success=False,
        message="Internal Server Error: Vui lòng thử lại sau.",
        data={"detail": str(exc)}
    )
    return JSONResponse(status_code=500, content=resp.model_dump())

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc: StarletteHTTPException):
    resp = APIResponse(success=False, message=str(exc.detail), data=None)
    return JSONResponse(status_code=exc.status_code, content=resp.model_dump())

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    resp = APIResponse(success=False, message="Dữ liệu không hợp lệ.", data={"errors": exc.errors()})
    return JSONResponse(status_code=422, content=resp.model_dump())


# ═══════════════════════════════════════════════════════════════════════════════
# API ROUTES — Cases
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/cases/create", summary="Tạo ca bệnh mới", response_model=APIResponse, tags=["Cases"])
async def create_case_endpoint(patient: PatientInput):
    logger.info(f"Khởi tạo ca mới cho bác sĩ {patient.bac_si_id}")

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
    await db.save_case(db_record)

    return APIResponse(
        success=True,
        message="Ca bệnh đã được khởi tạo",
        data={"case_id": case_id, "created_at": current_time}
    )


@app.post("/api/v1/cases/{case_id}/extract-and-triage", summary="Đánh giá toàn diện (AI)", response_model=APIResponse, tags=["AI Agents"])
async def comprehensive_triage_endpoint(case_id: str):
    logger.info(f"Bắt đầu trích xuất và đánh giá toàn diện cho case {case_id}")
    triage_result = await ai_service.process_triage(case_id)
    return APIResponse(
        success=triage_result.get("success", False),
        message=triage_result.get("message", "Processing completed"),
        data=triage_result.get("data")
    )


@app.post("/api/v1/cases/{case_id}/review", summary="Bác sĩ review & check rủi ro", response_model=APIResponse, tags=["AI Agents"])
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


@app.post("/api/v1/cases/{case_id}/evaluate-workflow", summary="Đánh giá luồng tiếp theo (Decision)", response_model=APIResponse, tags=["AI Agents"])
async def evaluate_workflow_endpoint(case_id: str):
    logger.info(f"Đánh giá workflow (Decision) cho case {case_id}")
    decision_result = await ai_service.evaluate_case_workflow(case_id)
    return APIResponse(
        success=decision_result.get("success", True),
        message=decision_result.get("message", "Đã đánh giá luồng"),
        data=decision_result.get("data")
    )


@app.post("/api/v1/cases/{case_id}/answers", summary="Nộp câu trả lời cho AI", response_model=APIResponse, tags=["AI Agents"])
async def submit_answers_endpoint(case_id: str, payload: NewAnswersInput):
    logger.info(f"Nhận câu trả lời bổ sung cho case {case_id}")
    answers_list = [{"question_id": a.question_id, "answer": a.answer} for a in payload.answers]
    answer_result = await ai_service.process_answers(case_id, answers_list)
    return APIResponse(
        success=answer_result.get("success", True),
        message=answer_result.get("message", "Đã cập nhật câu trả lời"),
        data=answer_result.get("data")
    )


@app.post("/api/v1/cases/{case_id}/doctor-approve", summary="Bác sĩ phê duyệt", response_model=APIResponse, tags=["Cases"])
async def doctor_approve_endpoint(case_id: str, payload: DoctorApproveInput):
    logger.info(f"Bác sĩ phê duyệt cho case {case_id}")

    start_time = time.time()
    update_data = {
        "Draft_Note": payload.draft_note,
        "Safety_Status": "approved_by_doctor",
        "SpO2_Final": payload.spo2,
        "HR_Final": payload.hr,
        "BP_Final": payload.bp
    }
    await db.update_case(case_id, update_data)
    await db.log_ai_interaction(case_id, "/cases/doctor-approve", round(float(time.time() - start_time), 2), "None", "Approved")

    return APIResponse(
        success=True,
        message="Đã lưu hồ sơ bệnh án thành công vào Excel",
        data={"case_id": case_id}
    )


# ═══════════════════════════════════════════════════════════════════════════════
# API ROUTES — Chat
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/chat", summary="Chat trực tiếp với AI (Đóng vai)", response_model=ChatResponse, tags=["Chat"])
@app.post("/api/v1/chat/", summary="Chat trực tiếp với AI (Đóng vai)", response_model=ChatResponse, tags=["Chat"], include_in_schema=False)
async def chat_endpoint(payload: ChatRequest):
    logger.info(f"Nhận yêu cầu Chat mới từ Role: {payload.user_role}")
    chat_result = await ai_service.process_chat(payload)
    return ChatResponse(reply=chat_result["reply"])


# ═══════════════════════════════════════════════════════════════════════════════
# API ROUTES — RAG
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/v1/rag/query", response_model=RAGQueryResponse, summary="Hỏi đáp RAG từ cơ sở dữ liệu bệnh", tags=["RAG — Knowledge Base"])
async def rag_query(req: RAGQueryRequest):
    logger.info(f"[RAG Router] query: {req.query[:80]}")
    try:
        result = await rag_service.query(req.query, top_k=req.top_k)
        return RAGQueryResponse(**result)
    except Exception as e:
        logger.error(f"[RAG Router] query error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/rag/health", summary="Kiểm tra trạng thái RAG service", tags=["RAG — Knowledge Base"])
async def rag_health():
    status = rag_service.get_status()
    return {
        "status": "ok" if rag_service.is_ready() else "degraded",
        "rag": status,
    }


@app.get("/api/v1/rag/stats", summary="Thống kê ChromaDB", tags=["RAG — Knowledge Base"])
async def rag_stats():
    return rag_service.get_status()


@app.post("/api/v1/rag/reload", summary="Reload dữ liệu từ Excel và reindex ChromaDB", tags=["RAG — Knowledge Base"])
async def rag_reload():
    logger.info("[RAG Router] reload triggered")
    result = await rag_service.reload()
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# BRIDGE — Kết nối MEdPilot-main
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/v1/medpilot/health", summary="Kiểm tra kết nối MEdPilot-main", tags=["Bridge — MEdPilot-main"])
async def medpilot_health():
    """Kiểm tra MEdPilot-main API có online không."""
    return await medpilot_bridge.check_medpilot_health()


@app.post("/api/v1/medpilot/query", summary="Proxy query tới MEdPilot-main RAG", response_model=APIResponse, tags=["Bridge — MEdPilot-main"])
async def medpilot_query(req: RAGQueryRequest):
    """Chuyển tiếp query sang MEdPilot-main để lấy kết quả RAG."""
    result = await medpilot_bridge.query_medpilot_rag(
        question=req.query,
        user_role="doctor",
        top_k=req.top_k or 3,
    )
    return APIResponse(
        success=result.get("success", False),
        message=result.get("answer", "Không có kết quả"),
        data=result,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# RUN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server...")
    port = int(os.getenv("BACKEND_PORT", "8080"))
    logger.info(f"Starting on port {port}...")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
