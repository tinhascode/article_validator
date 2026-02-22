from __future__ import annotations


from fastapi import FastAPI

from .user_routes import user_router


routers = [
    user_router,
]


def register_routes(app: FastAPI) -> None:
    for r in routers:
        app.include_router(r)
