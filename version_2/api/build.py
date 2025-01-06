from api.db.main import init_db
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator
from fastapi import FastAPI


@asynccontextmanager
async def life_span(app: FastAPI) -> AsyncGenerator:
    print("Starting Application...")
    await init_db()
    yield
    print("Shutting Down Application...")


def register_routes(app: FastAPI) -> None:
    pass
