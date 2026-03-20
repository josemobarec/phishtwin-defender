from fastapi import FastAPI
from datetime import datetime, timezone
import os

from app.db import check_db_connection

app = FastAPI(
    title="PhishTwin Defender API",
    version="0.1.0",
    description="Backend base para análisis defensivo de phishing y BEC."
)


@app.get("/")
def root():
    return {
        "message": "PhishTwin Defender API",
        "status": "running"
    }


@app.get("/health")
def health():
    db_ok, db_error = check_db_connection()

    return {
        "status": "ok" if db_ok else "degraded",
        "service": "api",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": os.getenv("APP_ENV", "development"),
        "database": {
            "connected": db_ok,
            "error": db_error
        }
    }