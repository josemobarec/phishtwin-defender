from datetime import datetime, timezone
import os

from fastapi import FastAPI, HTTPException

from app.db import check_db_connection
from app.models import (
    AnalyzeEmailRequest,
    AnalyzeEmailResponse,
    EmailSampleCreate,
    EmailSampleResponse,
)
from app.repository import insert_audit_log, insert_email_sample
from app.services.email_parser import parse_email_input

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


@app.post("/analyze-email", response_model=AnalyzeEmailResponse)
def analyze_email(payload: AnalyzeEmailRequest):
    has_eml = payload.eml_content is not None and payload.eml_content.strip() != ""
    has_json = payload.email_json is not None

    if not has_eml and not has_json:
        raise HTTPException(
            status_code=400,
            detail="Debes enviar 'eml_content' o 'email_json'."
        )

    if has_eml and has_json:
        raise HTTPException(
            status_code=400,
            detail="Envía solo uno: 'eml_content' o 'email_json', no ambos."
        )

    parsed_email = parse_email_input(payload.model_dump())

    sample_id = insert_email_sample({
        "source_type": parsed_email.raw_source_type,
        "source_name": payload.source_name,
        "subject": parsed_email.subject,
        "from_address": parsed_email.from_address,
        "from_domain": parsed_email.from_domain,
        "reply_to": parsed_email.reply_to,
        "message_id": parsed_email.message_id,
        "text_body": parsed_email.text_body,
        "html_body": parsed_email.html_body,
        "extracted_links": parsed_email.extracted_links,
        "metadata": {
            **payload.metadata,
            "headers": parsed_email.headers,
            "has_html": parsed_email.has_html,
            "has_links": parsed_email.has_links,
            "reply_to_mismatch": parsed_email.reply_to_mismatch,
            "raw_source_type": parsed_email.raw_source_type,
        }
    })

    insert_audit_log(
        actor="system-dev",
        action="analyze_email",
        target_type="email_sample",
        target_id=sample_id,
        details={
            "source_name": payload.source_name,
            "source_type": parsed_email.raw_source_type,
            "has_links": parsed_email.has_links,
            "has_html": parsed_email.has_html,
        }
    )

    return {
        "sample_id": sample_id,
        "parsed_email": parsed_email,
        "message": "Email analyzed and stored successfully"
    }