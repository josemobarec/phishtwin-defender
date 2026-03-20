from datetime import datetime, timezone
import os

from fastapi import FastAPI

from app.db import check_db_connection
from app.models import EmailSampleCreate, EmailSampleResponse
from app.repository import insert_audit_log, insert_email_sample

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


@app.post("/dev/email-sample", response_model=EmailSampleResponse)
def create_email_sample(payload: EmailSampleCreate):
    sample_id = insert_email_sample(payload.model_dump())

    insert_audit_log(
        actor="system-dev",
        action="create_email_sample",
        target_type="email_sample",
        target_id=sample_id,
        details={
            "source_type": payload.source_type,
            "subject": payload.subject
        }
    )

    return {
        "id": sample_id,
        "message": "Email sample stored successfully"
    }