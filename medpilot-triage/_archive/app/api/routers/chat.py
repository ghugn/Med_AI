from fastapi import APIRouter
from app.models.schemas import ChatRequest, ChatResponse
from app.services import ai_service
from app.core.logging import logger

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("", summary="Chat trực tiếp với AI (Đóng vai)", response_model=ChatResponse)
@router.post("/", summary="Chat trực tiếp với AI (Đóng vai)", response_model=ChatResponse, include_in_schema=False)
async def chat_endpoint(payload: ChatRequest):
    logger.info(f"Nhận yêu cầu Chat mới từ Role: {payload.user_role}")
    
    chat_result = await ai_service.process_chat(payload)
    
    return ChatResponse(
        reply=chat_result["reply"]
    )
