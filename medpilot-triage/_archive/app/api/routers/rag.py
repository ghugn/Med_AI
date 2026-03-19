"""
RAG Router — MedPilot
Các endpoint trực tiếp cho hệ thống RAG (query bệnh, stats, reload).
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services import rag_service
from app.core.logging import logger

router = APIRouter(prefix="/rag", tags=["RAG — Knowledge Base"])


# ─── Request / Response Models ─────────────────────────────────────────────────

class RAGQueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = None


class RAGQueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[str]
    latency: str
    context_chunks: int


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.post("/query", response_model=RAGQueryResponse, summary="Hỏi đáp RAG từ cơ sở dữ liệu bệnh")
async def rag_query(req: RAGQueryRequest):
    """
    Nhận câu hỏi → retrieve từ ChromaDB → gọi vLLM → trả về câu trả lời kèm nguồn tham khảo.
    """
    logger.info(f"[RAG Router] query: {req.query[:80]}")
    try:
        result = await rag_service.query(req.query, top_k=req.top_k)
        return RAGQueryResponse(**result)
    except Exception as e:
        logger.error(f"[RAG Router] query error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", summary="Kiểm tra trạng thái RAG service")
async def rag_health():
    """Trả về trạng thái khởi tạo RAG và số chunks đã index."""
    status = rag_service.get_status()
    return {
        "status": "ok" if rag_service.is_ready() else "degraded",
        "rag": status,
    }


@router.get("/stats", summary="Thống kê ChromaDB")
async def rag_stats():
    """Trả về số chunks, đường dẫn DB, trạng thái cache."""
    return rag_service.get_status()


@router.post("/reload", summary="Reload dữ liệu từ Excel và reindex ChromaDB")
async def rag_reload():
    """
    Force reload tất cả file .xlsx từ thư mục diseases_excel/ và reindex vào ChromaDB.
    Dùng khi cập nhật hoặc thêm file Excel mới.
    """
    logger.info("[RAG Router] reload triggered")
    result = await rag_service.reload()
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result
