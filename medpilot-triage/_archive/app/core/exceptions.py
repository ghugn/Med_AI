from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.logging import logger
from app.core.config import settings
from app.models.schemas import APIResponse

def setup_exception_handlers(app: FastAPI):
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Global exception: {str(exc)}", exc_info=True)
        resp = APIResponse(
            success=False,
            message="Internal Server Error: Vui lòng thử lại sau.",
            data={"detail": str(exc)} if settings.ENVIRONMENT == "dev" else None
        )
        return JSONResponse(status_code=500, content=resp.model_dump())

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        resp = APIResponse(
            success=False,
            message=str(exc.detail),
            data=None
        )
        return JSONResponse(status_code=exc.status_code, content=resp.model_dump())

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        resp = APIResponse(
            success=False,
            message="Dữ liệu không hợp lệ.",
            data={"errors": exc.errors()}
        )
        return JSONResponse(status_code=422, content=resp.model_dump())
