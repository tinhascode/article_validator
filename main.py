from fastapi import FastAPI, HTTPException
from src.config.settings import init_db
from src.routes import register_routes
from src.exceptions import BaseServiceException
from src.utils.exception_handlers import (
    service_exception_handler,
    http_exception_handler,
    general_exception_handler,
)


def create_app() -> FastAPI:
    """Create a FastAPI application instance"""
    fastapi_app = FastAPI(
        title="Article Validator API",
        version="0.1.0",
        description="API for validating and managing articles",
    )

    fastapi_app.add_exception_handler(BaseServiceException, service_exception_handler)
    fastapi_app.add_exception_handler(HTTPException, http_exception_handler)
    fastapi_app.add_exception_handler(Exception, general_exception_handler)

    @fastapi_app.on_event("startup")
    def _init_db_on_startup() -> None:
        """Initialize the database on application startup."""
        init_db()

    register_routes(fastapi_app)

    return fastapi_app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )