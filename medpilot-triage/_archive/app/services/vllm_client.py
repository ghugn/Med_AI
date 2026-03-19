"""
vLLM Async Client — MedPilot
Gọi vLLM server qua chuẩn OpenAI-compatible API (/v1/chat/completions).
"""
import httpx
import json
from typing import List, Dict, Optional
from app.core.config import settings
from app.core.logging import logger


async def chat_completion(
    messages: List[Dict[str, str]],
    max_tokens: int = 1024,
    temperature: float = 0.3,
    timeout: float = None,
) -> str:
    """
    Gọi vLLM /v1/chat/completions và trả về text trả lời.

    Args:
        messages: List message theo định dạng OpenAI [{"role": ..., "content": ...}]
        max_tokens: Giới hạn token output
        temperature: Độ ngẫu nhiên (0.0 = deterministic)
        timeout: Timeout tính bằng giây (None = dùng config mặc định)

    Returns:
        Chuỗi text trả lời từ model, hoặc raise exception nếu lỗi nghiêm trọng
    """
    url = f"{settings.VLLM_BASE_URL}/chat/completions"
    payload = {
        "model": settings.VLLM_MODEL_NAME,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
    }
    _timeout = timeout if timeout is not None else settings.VLLM_TIMEOUT

    logger.info(f"[vLLM] POST {url} | model={settings.VLLM_MODEL_NAME} | msgs={len(messages)}")

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, timeout=_timeout)

    if response.status_code != 200:
        logger.error(f"[vLLM] HTTP {response.status_code}: {response.text[:300]}")
        raise httpx.HTTPStatusError(
            f"vLLM trả về lỗi {response.status_code}",
            request=response.request,
            response=response,
        )

    data = response.json()
    try:
        text = data["choices"][0]["message"]["content"]
        logger.info(f"[vLLM] OK — {len(text)} chars")
        return text
    except (KeyError, IndexError) as e:
        logger.error(f"[vLLM] Parse lỗi: {e} | raw: {str(data)[:300]}")
        raise ValueError(f"Không thể parse response từ vLLM: {e}")


async def chat_completion_safe(
    messages: List[Dict[str, str]],
    fallback: str = "Xin lỗi, hệ thống AI hiện không khả dụng. Vui lòng thử lại sau.",
    max_tokens: int = 1024,
    temperature: float = 0.3,
    timeout: float = None,
) -> str:
    """
    Gọi chat_completion, trả về `fallback` nếu có bất kỳ lỗi nào (không raise exception).
    Dùng cho các luồng không muốn crash toàn bộ request.
    """
    try:
        return await chat_completion(messages, max_tokens, temperature, timeout)
    except Exception as e:
        logger.warning(f"[vLLM] Lỗi kết nối/parse, dùng fallback. Chi tiết: {e}")
        return fallback
