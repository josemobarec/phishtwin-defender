from fastapi import FastAPI
from datetime import datetime, timezone
import os

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
    return {
        "status": "ok",
        "service": "api",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": os.getenv("APP_ENV", "development")
    }