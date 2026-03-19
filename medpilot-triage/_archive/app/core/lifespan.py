from contextlib import asynccontextmanager
from fastapi import FastAPI
import asyncio
from app.db.excel_db import init_db
from app.core.config import settings
from app.core.logging import logger
from app.services import rag_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting API in {settings.ENVIRONMENT.upper()} mode...")
    
    # Initialize DB (which merges Excel data with JSON context)
    init_db()

    # Load RAG asynchronously
    logger.info("[RAG] Bắt đầu khởi tạo RAG service...")
    loop = asyncio.get_running_loop()
    success = await loop.run_in_executor(None, rag_service.initialize)
    if success:
        logger.info("[RAG] ✅ RAG service sẵn sàng")
    else:
        logger.warning(
            "[RAG] ⚠️ RAG service khởi tạo không thành công "
            "(có thể thiếu package hoặc Excel folder trống). "
            "Backend vẫn hoạt động bình thường, chỉ endpoint /rag/query sẽ trả warning."
        )
        
    yield
    
    logger.info("Hoàn tất dọn dẹp (nếu cần thiết). API shutdown an toàn.")
