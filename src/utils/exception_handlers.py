from __future__ import annotations

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from src.exceptions.base_exception import BaseServiceException
from src.config.logger import get_logger

logger = get_logger("ExceptionHandlers")

async def service_exception_handler(request: Request, exc: BaseServiceException) -> JSONResponse:
    logger.warning(
        "Service exception '%s' raised: %s (status: %d)", 
        exc.__class__.__name__,
        exc.message, 
        exc.status_code
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "detail": exc.detail,
        },
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    logger.warning(
        "HTTP exception raised: %s (status: %d)", 
        exc.detail,
        exc.status_code
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "detail": exc.detail,
            "type": "HTTPException",
        },
    )

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception: %s", str(exc))
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred. Please try again later.",
            "type": "InternalServerError",
        },
    )