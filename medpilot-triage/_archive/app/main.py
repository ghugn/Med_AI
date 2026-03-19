from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routers import cases, chat, rag
from app.core.config import settings
from app.core.logging import logger

from app.core.exceptions import setup_exception_handlers
from app.core.lifespan import lifespan
from app.core.static import setup_static_serving

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version="1.0.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        lifespan=lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ─── Global Exception Handlers ──────────────────────────────────────────
    setup_exception_handlers(app)

    # ─── Routers ────────────────────────────────────────────────────────────
    app.include_router(cases.router, prefix="/api/v1")
    app.include_router(chat.router, prefix="/api/v1")
    app.include_router(rag.router, prefix="/api/v1")
    
    # Serve static files (frontend)
    setup_static_serving(app)

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)

