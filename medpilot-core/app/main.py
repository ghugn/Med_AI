"""
MedPilot-Core API — Synced with Next.js Frontend
Mode: QnA DEMO (trả về dữ liệu demo từ qna_demo.json)
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

import app.db as db
from app.routers import scribe, reminder, chat, cases
from app.services.qna_service import get_qna_service

# Logging Setup
logging.basicConfig(level="INFO", format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MedPilot Core API",
    description="Backend cho frontend MedPilot — Scribe, Reminder, Chat",
    version="2.0",
)

# CORS Configuration - Restricted
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Lỗi máy chủ nội bộ. Vui lòng thử lại sau.", "error": str(exc)}
    )

logger.info("✅ Backend ready! (MOCK + QnA DEMO MODE)")

# Init DB and Load QnA Data
@app.on_event("startup")
async def startup_event():
    db.init_db()
    # Pre-load QnA Service
    qna_service = get_qna_service()
    qna_service.load_data()

# Include Routers
app.include_router(scribe.router)
app.include_router(reminder.router)
app.include_router(chat.router)
app.include_router(cases.router)

@app.get("/api/health", tags=["Health"])
async def health():
    qna_service = get_qna_service()
    return {
        "status": "ok", 
        "mode": "demo_qna", 
        "patient_qna_count": len(qna_service.patient_qna)
    }