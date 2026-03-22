from datetime import datetime, timezone
import os

from fastapi import FastAPI, HTTPException

from app.db import check_db_connection
from app.models import (
    AnalyzeEmailRequest,
    AnalyzeEmailResponse,
    DetectionRecord,
    EmailSampleCreate,
    EmailSampleListResponse,
    EmailSampleRecord,
    EmailSampleResponse,
    FeedbackRequest,
    FeedbackResponse,
    DetectionListItem,
    DetectionListResponse,
)
from app.repository import (
    get_email_sample_by_id,
    insert_analyst_feedback,
    insert_audit_log,
    insert_detection,
    insert_email_sample,
    list_email_samples,
    get_detection_by_id,
    list_detections,
)
from app.services.detection_rules import evaluate_detection_rules
from app.services.email_parser import parse_email_input
from app.services.explainability import build_detection_explanation
from app.services.scoring import calculate_risk_score

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

    # 1. Parseo
    parsed_email = parse_email_input(payload.model_dump())
    parsed_email_dict = parsed_email.model_dump()

    # 2. Guardar sample parseado
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

    # 3. Reglas
    signals = evaluate_detection_rules(parsed_email_dict)

    # 4. Scoring
    score_result = calculate_risk_score(signals)

    # 5. Explicación
    explanation = build_detection_explanation(
        parsed_email=parsed_email_dict,
        signals=signals,
        score_result=score_result,
    )

    # 6. Preparar detection payload real
    detection_payload = {
        "email_sample_id": sample_id,
        "verdict": score_result["verdict"],
        "risk_score": score_result["risk_score"],
        "confidence": score_result["confidence"],
        "reasoning_summary": explanation["reasoning_summary"],
        "detected_signals": [signal.model_dump() for signal in signals],
        "recommended_action": explanation["recommended_action"],
        "model_versions": {
            "parser": "v0.1.0",
            "ruleset": "v0.1.0",
            "scoring": "v0.1.0",
            "explainability": "v0.1.0",
        },
        "evidence": explanation["evidence"],
    }

    # 7. Persistir detección
    detection_id = insert_detection(detection_payload)

    # 8. Auditoría
    insert_audit_log(
        actor="system-dev",
        action="analyze_email",
        target_type="email_sample",
        target_id=sample_id,
        details={
            "source_name": payload.source_name,
            "source_type": parsed_email.raw_source_type,
            "verdict": score_result["verdict"],
            "risk_score": score_result["risk_score"],
            "signal_count": len(signals),
            "detection_id": detection_id,
        }
    )

    # 9. Respuesta
    return {
        "sample_id": sample_id,
        "detection_id": detection_id,
        "parsed_email": parsed_email,
        "detection": {
            "id": detection_id,
            "email_sample_id": sample_id,
            "verdict": detection_payload["verdict"],
            "risk_score": detection_payload["risk_score"],
            "confidence": detection_payload["confidence"],
            "reasoning_summary": detection_payload["reasoning_summary"],
            "detected_signals": detection_payload["detected_signals"],
            "recommended_action": detection_payload["recommended_action"],
            "model_versions": detection_payload["model_versions"],
            "evidence": detection_payload["evidence"],
        },
        "message": "Email analyzed and stored successfully"
    }

@app.get("/email-samples", response_model=EmailSampleListResponse)
def get_email_samples():
    items = list_email_samples()
    return {
        "items": items,
        "total": len(items)
    }


@app.get("/email-samples/{sample_id}", response_model=EmailSampleRecord)
def get_email_sample(sample_id: int):
    item = get_email_sample_by_id(sample_id)

    if not item:
        raise HTTPException(status_code=404, detail="Email sample not found.")

    return item


@app.post("/feedback", response_model=FeedbackResponse)
def create_feedback(payload: FeedbackRequest):
    feedback_id = insert_analyst_feedback(payload.model_dump())

    insert_audit_log(
        actor=payload.analyst_email,
        action="create_feedback",
        target_type="detection",
        target_id=payload.detection_id,
        details={
            "corrected_verdict": payload.corrected_verdict,
            "useful": payload.useful,
        }
    )

    return {
        "feedback_id": feedback_id,
        "message": "Feedback stored successfully"
    }

@app.get("/detections", response_model=DetectionListResponse)
def get_detections():
    items = list_detections()
    return {
        "items": items,
        "total": len(items)
    }


@app.get("/detections/{detection_id}", response_model=DetectionRecord)
def get_detection(detection_id: int):
    item = get_detection_by_id(detection_id)

    if not item:
        raise HTTPException(status_code=404, detail="Detection not found.")

    return item