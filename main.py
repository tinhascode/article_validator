from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.config.settings import get_db, get_settings, Settings, init_db
from src.routes import register_routes


def create_app() -> FastAPI:
    app = FastAPI(
        title="Article Validator API",
        version="0.1.0",
        description="API for validating and managing articles",
    )

    @app.on_event("startup")
    def _init_db_on_startup() -> None:
        init_db()

    register_routes(app)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )