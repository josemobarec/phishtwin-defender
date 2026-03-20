from fastapi import FastAPI
from sqlmodel import SQLModel

from app.api.routes import detections, health
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.session import engine
from app.models import entities  # noqa: F401

setup_logging()
settings = get_settings()
app = FastAPI(title=settings.app_name, version="0.1.0")


@app.on_event("startup")
def on_startup() -> None:
    SQLModel.metadata.create_all(engine)


app.include_router(health.router, prefix=settings.api_v1_prefix, tags=["system"])
app.include_router(detections.router, prefix=settings.api_v1_prefix, tags=["detections"])
