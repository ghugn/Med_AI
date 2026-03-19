"""
MedPilot Bridge — Kết nối backend_AI → MEdPilot-main API
Cho phép backend_AI gọi RAG/Query/Chat từ project chính MEdPilot-main.
"""
import os
import httpx
import logging
from typing import Optional, Dict

logger = logging.getLogger("medpilot")

# URL gốc của MEdPilot-main API (đọc từ .env hoặc mặc định)
MEDPILOT_API_URL = os.getenv("MEDPILOT_API_URL", "http://localhost:8000/api/v1")
BRIDGE_TIMEOUT = 60.0


async def check_medpilot_health() -> Dict:
    """Kiểm tra MEdPilot-main có đang chạy không."""
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{MEDPILOT_API_URL}/ask-role",
                timeout=10.0
            )
            if resp.status_code == 200:
                return {"status": "online", "url": MEDPILOT_API_URL}
            return {"status": "error", "code": resp.status_code, "url": MEDPILOT_API_URL}
    except Exception as e:
        return {"status": "offline", "error": str(e), "url": MEDPILOT_API_URL}


async def query_medpilot_rag(
    question: str,
    user_role: str = "doctor",
    top_k: int = 3,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
) -> Dict:
    """
    Gọi /api/v1/query của MEdPilot-main để RAG retrieve + LLM answer.
    
    Args:
        question: Câu hỏi cần hỏi
        user_role: "doctor" hoặc "patient"
        top_k: Số lượng kết quả retrieve
    
    Returns:
        Dict với keys: query, answer, retrieved_chunks, latency, success
    """
    url = f"{MEDPILOT_API_URL}/query?role={user_role}"
    payload = {
        "query": question,
        "user_role": user_role,
        "top_k": top_k,
    }
    if max_tokens:
        payload["max_tokens"] = max_tokens
    if temperature:
        payload["temperature"] = temperature

    logger.info(f"[Bridge] POST {url} | query={question[:60]}...")

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, timeout=BRIDGE_TIMEOUT)
        
        if resp.status_code == 200:
            data = resp.json()
            logger.info(f"[Bridge] OK — answer length: {len(data.get('answer', ''))}")
            return data
        else:
            logger.error(f"[Bridge] HTTP {resp.status_code}: {resp.text[:200]}")
            return {
                "query": question,
                "answer": f"Lỗi từ MEdPilot-main: HTTP {resp.status_code}",
                "retrieved_chunks": 0,
                "latency": 0,
                "success": False,
            }
    except httpx.ConnectError:
        logger.warning("[Bridge] Không thể kết nối MEdPilot-main. Server có đang chạy?")
        return {
            "query": question,
            "answer": "⚠️ Không thể kết nối MEdPilot-main. Hãy đảm bảo server đang chạy trên port 8000.",
            "retrieved_chunks": 0,
            "latency": 0,
            "success": False,
        }
    except Exception as e:
        logger.error(f"[Bridge] Lỗi không xác định: {e}")
        return {
            "query": question,
            "answer": f"Lỗi bridge: {str(e)}",
            "retrieved_chunks": 0,
            "latency": 0,
            "success": False,
        }


async def chat_medpilot(
    message: str,
    conversation_id: Optional[str] = None,
    top_k: int = 3,
) -> Dict:
    """
    Gọi /api/v1/chat của MEdPilot-main cho patient chat.
    
    Returns:
        Dict với keys: message, is_dermatology, conversation_id, ...
    """
    url = f"{MEDPILOT_API_URL}/chat"
    payload = {
        "message": message,
        "top_k": top_k,
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id

    logger.info(f"[Bridge] POST {url} | message={message[:60]}...")

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, timeout=BRIDGE_TIMEOUT)
        
        if resp.status_code == 200:
            data = resp.json()
            logger.info(f"[Bridge] Chat OK — reply length: {len(data.get('message', ''))}")
            return data
        else:
            logger.error(f"[Bridge] Chat HTTP {resp.status_code}: {resp.text[:200]}")
            return {
                "message": f"Lỗi chat từ MEdPilot-main: HTTP {resp.status_code}",
                "success": False,
            }
    except httpx.ConnectError:
        return {
            "message": "⚠️ Không thể kết nối MEdPilot-main cho chat.",
            "success": False,
        }
    except Exception as e:
        return {
            "message": f"Lỗi bridge chat: {str(e)}",
            "success": False,
        }
