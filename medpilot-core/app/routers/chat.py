from fastapi import APIRouter
import time
import uuid
import logging

from app.schemas import ChatRequest, ChatResponse
from app.services.qna_service import get_qna_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Chat"])

_EMERGENCY_KEYWORDS = ["khó thở", "sưng môi", "sưng lưỡi", "ngất", "sốc", "cấp cứu", "phản vệ"]

_EMERGENCY_RESPONSE = {
    "answer": (
        "🚨 **CẢNH BÁO KHẨN CẤP!**\n\n"
        "Dựa trên mô tả của bạn, tình trạng này CÓ THỂ cần được xử lý y tế ngay lập tức.\n\n"
        "**Hãy đến phòng cấp cứu NGAY nếu bạn có:**\n"
        "- Khó thở, sưng mặt/môi/lưỡi\n"
        "- Phát ban lan nhanh toàn thân\n"
        "- Sốt cao kèm phát ban\n"
        "- Chóng mặt, ngất xỉu\n\n"
        "📞 **Gọi 115 ngay** nếu có bất kỳ triệu chứng nào ở trên!"
    ),
    "safety_notice": "⚠️ Đây CÓ THỂ là tình huống khẩn cấp. Hãy đến bệnh viện NGAY.",
    "possible_topics": ["Dị ứng cấp tính", "Phản vệ", "Nhiễm trùng nặng"],
    "when_to_seek_care": ["NGAY LẬP TỨC — không nên chờ đợi"],
    "red_flag_advice": [
        "Khó thở hoặc sưng phù → gọi cấp cứu 115",
        "Sốt cao > 39°C kèm phát ban → đến bệnh viện ngay",
    ],
    "confidence_level": "high",
    "requires_emergency_care": True,
}

@router.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """Hỏi đáp da liễu cho bệnh nhân — sử dụng bộ QnA DEMO."""
    logger.info(f"[Chat] QnA DEMO question='{req.question[:60]}...'")
    start = time.time()

    question_lower = req.question.lower()

    # 1. Check emergency keywords
    is_emergency = any(kw in question_lower for kw in _EMERGENCY_KEYWORDS)
    if is_emergency:
        data = _EMERGENCY_RESPONSE
        logger.info("[Chat] Emergency keywords detected")
    else:
        # 2. Find best matching QnA via QnAService
        qna_service = get_qna_service()
        data = qna_service.find_best_match(req.question, threshold=0.75)

        # 3. RAG Fallback if QnA yields no good match
        if data == qna_service.default_answer or data.get("confidence_level") == "low" or "Xin lỗi" in data.get("answer", ""):
            logger.info("[Chat] Falling back to RAG...")
            from app.rag_engine import RAGEngine
            from app.llm_service import LLMService
            from app.config import settings
            
            rag_engine = RAGEngine(
                diseases_json=settings.DISEASES_JSON,
                db_path=settings.DB_PATH,
                embedding_model=settings.EMBEDDING_MODEL
            )
            llm_service = LLMService(
                api_url=settings.LLM_API_URL,
                model=settings.VLLM_MODEL if "/v1/" in settings.LLM_API_URL else settings.OLLAMA_MODEL,
                timeout=settings.TIMEOUT
            )
            
            retrieved = rag_engine.retrieve(req.question, top_k=3)
            context_str = "\n".join([f"Bệnh: {doc['disease']}\nNội dung: {doc['content']}" for doc in retrieved])
            
            sys_msg = {"role": "system", "content": "Bạn là trợ lý y tế. Trả lời người dùng bằng tiếng Việt thân thiện, rõ ràng, dựa trên ngữ cảnh được cung cấp. Cấm tự chẩn đoán bệnh chắc chắn."}
            user_msg = {"role": "user", "content": f"Ngữ cảnh y khoa:\n{context_str}\n\nCâu hỏi: {req.question}"}
            
            llm_result = llm_service.query([sys_msg, user_msg])
            
            if llm_result["success"] and llm_result["answer"]:
                data = {
                    "answer": llm_result["answer"],
                    "safety_notice": "⚠️ Câu trả lời này được AI tự động tạo ra từ cơ sở dữ liệu. Vui lòng tham khảo ý kiến Bác sĩ.",
                    "confidence_level": "medium",
                    "source_evidence": list(set([doc['disease'] for doc in retrieved])),
                    "possible_topics": [],
                    "when_to_seek_care": [],
                    "red_flag_advice": [],
                    "requires_emergency_care": False
                }
            else:
                data["answer"] += f"\n\n(RAG Fallback LLM Status: {llm_result['error']})"

    # 3. Handle UUID to avoid Pyre string slice lint
    new_id = str(uuid.uuid4()).split("-")[0]

    response = ChatResponse(
        request_id=req.request_id or f"req_chat_{new_id}",
        question=req.question,
        answer=data.get("answer", ""),
        safety_notice=data.get("safety_notice", ""),
        possible_topics=data.get("possible_topics", []),
        when_to_seek_care=data.get("when_to_seek_care", []),
        red_flag_advice=data.get("red_flag_advice", []),
        source_evidence=data.get("source_evidence", ["Cơ sở dữ liệu DermNet Vietnamese"]),
        confidence_level=data.get("confidence_level", "medium"),
        requires_doctor_followup=True,
        requires_emergency_care=data.get("requires_emergency_care", False),
        latency_ms=round((time.time() - start) * 1000),
        model_version="demo_v1",
    )

    logger.info(f"[Chat] Done in {response.latency_ms}ms")
    return response
