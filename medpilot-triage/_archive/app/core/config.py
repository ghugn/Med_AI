import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "MedPilot API (Demo POC)"
    PROJECT_DESCRIPTION: str = "Backend trung chuyển cho trợ lý AI y khoa MedPilot. Tích hợp Safety Layer & Logging."
    ENVIRONMENT: str = "dev"
    
    # Database
    DB_FILE: str = "database.xlsx"
    
    # Tên các cột trong Excel File (Chỉ chứa metadata chính, dữ liệu chi tiết ở JSON)
    DB_HEADERS: list[str] = [
        "Case_ID", "Ngày_giờ_khám", "Bác_sĩ_ID", "Họ_tên_BN", "Tuổi", "Giới_tính",
        "Red_Flag", "Uncertainty_Score", "Safety_Status",
        "SpO2_Final", "HR_Final", "BP_Final"
    ]
    
    # FastAI (legacy, kept for compatibility)
    FASTAI_API_ENDPOINT: str = "http://localhost:8001/api/v1/extract"
    FASTAI_API_KEY: str = "your-fastai-api-key-here"

    # ─── vLLM (OpenAI-compatible local model server) ───────────────────────
    # Chạy vLLM: python -m vllm.entrypoints.openai.api_server --model <model_name> --port 8001
    VLLM_BASE_URL: str = "http://localhost:8001/v1"
    # Đặt tên model đúng với model đang được serve trên vLLM
    VLLM_MODEL_NAME: str = "default"
    # Timeout (giây) cho mỗi request đến vLLM
    VLLM_TIMEOUT: float = 180.0

    # ─── RAG (Excel → ChromaDB + sentence-transformers) ────────────────────
    # Thư mục chứa file .xlsx bệnh (mỗi file = 1 bệnh, mỗi cột = 1 trường)
    RAG_EXCEL_FOLDER: str = "./diseases_excel"
    # Thư mục lưu ChromaDB vector store
    RAG_DB_PATH: str = "./medpilot_db"
    # Thư mục lưu cache pickle
    RAG_CACHE_PATH: str = "./medpilot_cache"
    # Số chunks tối đa lấy làm context mỗi lần retrieve
    RAG_TOP_K: int = 3

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()
