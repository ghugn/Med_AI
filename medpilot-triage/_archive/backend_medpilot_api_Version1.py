"""
MedPilot Backend API
Integrates RAG module with FastAPI
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
import os
from medpilot_rag_module import MedPilotRAGModule

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MedPilot Backend API",
    description="Medical disease RAG system",
    version="1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG module
excel_folder = os.getenv("EXCEL_FOLDER", "./diseases_excel")
chat_api_url = os.getenv("CHAT_API_URL", "http://localhost:8001/v1/chat/completions")

rag_module = MedPilotRAGModule(
    excel_folder=excel_folder,
    chat_api_url=chat_api_url
)

# Load diseases
logger.info("Loading diseases...")
diseases = rag_module.load_diseases()

# Index diseases
logger.info("Indexing diseases...")
rag_module.index_diseases(diseases)

# ============ REQUEST MODELS ============
class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3

class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[str]
    latency: str

# ============ ENDPOINTS ============
@app.post("/api/v1/query", response_model=QueryResponse)
async def query(req: QueryRequest):
    """Query the RAG system"""
    try:
        result = rag_module.query(req.query)
        return QueryResponse(**result)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/health")
async def health():
    """Health check"""
    stats = rag_module.get_stats()
    return {
        "status": "ok",
        "stats": stats
    }

@app.get("/api/v1/stats")
async def stats():
    """Get system stats"""
    return rag_module.get_stats()

@app.post("/api/v1/reload")
async def reload():
    """Reload data from Excel"""
    try:
        diseases = rag_module.load_diseases(force_reload=True)
        rag_module.index_diseases(diseases, force_reindex=True)
        return {
            "status": "ok",
            "message": f"Reloaded {len(diseases)} diseases"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )