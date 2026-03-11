from fastapi import  FastAPI
from src.config.settings import init_db
from src.routes import register_routes


def create_app() -> FastAPI:
    """Create a FastAPI application instance"""
    fastapi_app = FastAPI(
        title="Article Validator API",
        version="0.1.0",
        description="API for validating and managing articles",
    )

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