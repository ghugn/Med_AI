"""
RAG Service — MedPilot PoC
Singleton adapter: Load Excel → ChromaDB → query → vLLM.
"""
import asyncio
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional
import ai_prompts

logger = logging.getLogger("medpilot")

# ─── Config ──────────────────────────────────────────────────────────────────

RAG_EXCEL_FOLDER = "./diseases_excel"
RAG_DB_PATH = "./medpilot_db"
RAG_CACHE_PATH = "./medpilot_cache"
RAG_TOP_K = 3

# ─── Singleton state ─────────────────────────────────────────────────────────

_rag_module = None
_rag_initialized = False
_rag_error: Optional[str] = None


def _get_rag_module():
    """Lazy-load MedPilotRAGModule."""
    try:
        from rag_module import MedPilotRAGModule
        return MedPilotRAGModule
    except ImportError as e:
        logger.error(f"[RAG] Không thể import MedPilotRAGModule: {e}")
        return None


def initialize() -> bool:
    """Khởi tạo RAG module (đồng bộ, gọi từ startup event)."""
    global _rag_module, _rag_initialized, _rag_error

    excel_folder = Path(RAG_EXCEL_FOLDER)
    if not excel_folder.exists():
        logger.warning(f"[RAG] Thư mục Excel không tồn tại: {excel_folder}")
        logger.warning("[RAG] Tạo thư mục rỗng. Thêm file .xlsx để RAG hoạt động.")
        excel_folder.mkdir(parents=True, exist_ok=True)

    excel_files = list(excel_folder.glob("*.xlsx")) + list(excel_folder.glob("*.xls"))

    MedPilotRAGModule = _get_rag_module()
    if MedPilotRAGModule is None:
        _rag_error = "Thiếu package: chromadb hoặc sentence-transformers. Chạy: pip install chromadb sentence-transformers"
        logger.error(f"[RAG] {_rag_error}")
        return False

    try:
        logger.info("[RAG] Khởi tạo RAG module...")
        _rag_module = MedPilotRAGModule(
            excel_folder=str(excel_folder),
            db_path=str(RAG_DB_PATH),
            cache_path=str(RAG_CACHE_PATH),
            chat_api_url=f"{ai_prompts.VLLM_BASE_URL}/chat/completions",
            top_k=RAG_TOP_K,
        )

        if excel_files:
            logger.info(f"[RAG] Tìm thấy {len(excel_files)} file Excel, bắt đầu load + index...")
            diseases = _rag_module.load_diseases()
            _rag_module.index_diseases(diseases)
            logger.info(f"[RAG] ✅ Đã index {len(diseases)} bệnh")
        else:
            logger.warning("[RAG] Không có file Excel → ChromaDB trống. Đặt file .xlsx vào: " + str(excel_folder))

        _rag_initialized = True
        _rag_error = None
        return True

    except Exception as e:
        _rag_error = str(e)
        logger.error(f"[RAG] Lỗi khởi tạo: {e}", exc_info=True)
        return False


def is_ready() -> bool:
    return _rag_initialized and _rag_module is not None


def get_status() -> Dict:
    """Trả về trạng thái RAG service."""
    status = {
        "initialized": _rag_initialized,
        "error": _rag_error,
        "excel_folder": str(RAG_EXCEL_FOLDER),
        "db_path": str(RAG_DB_PATH),
    }
    if is_ready():
        try:
            stats = _rag_module.get_stats()
            status.update(stats)
        except Exception as e:
            status["stats_error"] = str(e)
    return status


async def query(question: str, top_k: Optional[int] = None) -> Dict:
    """Full RAG pipeline: retrieve → build prompt → gọi vLLM."""
    start = time.time()
    k = top_k or RAG_TOP_K

    if not is_ready():
        return {
            "query": question,
            "answer": "⚠️ Hệ thống RAG chưa sẵn sàng. Kiểm tra log để biết nguyên nhân.",
            "sources": [],
            "latency": "0s",
            "context_chunks": [],
        }

    loop = asyncio.get_event_loop()
    retrieved = await loop.run_in_executor(None, lambda: _rag_module.retrieve(question, top_k=k))

    if not retrieved:
        context = ""
        sources = []
    else:
        context = "\n\n".join([
            f"[{r['disease']} - {r['field']}]\n{r['content']}"
            for r in retrieved
        ])
        sources = list(dict.fromkeys(r["disease"] for r in retrieved))

    # Build messages
    messages = _build_rag_messages(question, context)

    if context:
        answer = await ai_prompts.chat_completion_safe(
            messages=messages,
            fallback=(
                "Không thể kết nối đến LLM. "
                "Thông tin tham khảo từ RAG:\n\n" + context[:1000]
            ),
            max_tokens=1024,
        )
    else:
        messages_general = _build_general_messages(question)
        answer = await ai_prompts.chat_completion_safe(
            messages=messages_general,
            fallback="Không tìm thấy thông tin trong cơ sở dữ liệu và không thể kết nối LLM.",
            max_tokens=512,
        )

    latency = f"{time.time() - start:.2f}s"
    logger.info(f"[RAG] query done in {latency} | sources: {sources}")

    return {
        "query": question,
        "answer": answer,
        "sources": sources,
        "latency": latency,
        "context_chunks": len(retrieved),
    }


async def reload() -> Dict:
    """Force reload dữ liệu từ Excel và reindex ChromaDB."""
    global _rag_initialized, _rag_error

    if _rag_module is None:
        success = initialize()
        return {
            "status": "ok" if success else "error",
            "message": "RAG khởi tạo lại thành công" if success else _rag_error,
        }

    try:
        loop = asyncio.get_event_loop()
        diseases = await loop.run_in_executor(
            None, lambda: _rag_module.load_diseases(force_reload=True)
        )
        await loop.run_in_executor(
            None, lambda: _rag_module.index_diseases(diseases, force_reindex=True)
        )
        _rag_initialized = True
        _rag_error = None
        return {"status": "ok", "message": f"Đã reload {len(diseases)} bệnh từ Excel"}
    except Exception as e:
        _rag_error = str(e)
        logger.error(f"[RAG] Lỗi reload: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


# ─── Private helpers ─────────────────────────────────────────────────────────

def _build_rag_messages(query: str, context: str) -> List[Dict]:
    system = (
        "Bạn là một trợ lý y tế chuyên nghiệp của hệ thống MedPilot. "
        "Hãy trả lời câu hỏi dựa trên thông tin tham khảo được cung cấp. "
        "Nếu thông tin không đủ, hãy nói rõ ràng. "
        "Không tự ý chẩn đoán hay kê đơn thuốc cụ thể. "
        "Sử dụng tiếng Việt chuẩn."
    )
    user = (
        f"=== THÔNG TIN THAM KHẢO ===\n{context}\n\n"
        f"=== CÂU HỎI ===\n{query}\n\n"
        "=== TRẢ LỜI ==="
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def _build_general_messages(query: str) -> List[Dict]:
    system = (
        "Bạn là một trợ lý y tế chuyên nghiệp. "
        "Không tìm thấy thông tin trong cơ sở dữ liệu nội bộ, nhưng hãy trả lời "
        "dựa trên kiến thức y khoa tổng quát của bạn. "
        "Luôn kèm disclaimer: 'Thông tin mang tính tham khảo, vui lòng tham khảo bác sĩ chuyên khoa.' "
        "Không kê đơn thuốc cụ thể. Sử dụng tiếng Việt."
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": query},
    ]
