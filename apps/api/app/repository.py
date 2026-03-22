import json
from typing import Any, Dict

from app.db import get_db_connection


def insert_email_sample(payload: Dict[str, Any]) -> int:
    query = """
        INSERT INTO email_samples (
            source_type,
            source_name,
            subject,
            from_address,
            from_domain,
            reply_to,
            message_id,
            text_body,
            html_body,
            extracted_links,
            metadata
        )
        VALUES (
            %(source_type)s,
            %(source_name)s,
            %(subject)s,
            %(from_address)s,
            %(from_domain)s,
            %(reply_to)s,
            %(message_id)s,
            %(text_body)s,
            %(html_body)s,
            %(extracted_links)s::jsonb,
            %(metadata)s::jsonb
        )
        RETURNING id;
    """

    db_payload = {
        "source_type": payload.get("source_type", "json"),
        "source_name": payload.get("source_name"),
        "subject": payload.get("subject"),
        "from_address": payload.get("from_address"),
        "from_domain": payload.get("from_domain"),
        "reply_to": payload.get("reply_to"),
        "message_id": payload.get("message_id"),
        "text_body": payload.get("text_body"),
        "html_body": payload.get("html_body"),
        "extracted_links": json.dumps(payload.get("extracted_links", [])),
        "metadata": json.dumps(payload.get("metadata", {})),
    }

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, db_payload)
            inserted_id = cur.fetchone()[0]
        conn.commit()

    return inserted_id


def insert_audit_log(
    actor: str,
    action: str,
    target_type: str,
    target_id: int,
    details: Dict[str, Any]
) -> None:
    query = """
        INSERT INTO audit_logs (
            actor,
            action,
            target_type,
            target_id,
            details
        )
        VALUES (
            %(actor)s,
            %(action)s,
            %(target_type)s,
            %(target_id)s,
            %(details)s::jsonb
        );
    """

    db_payload = {
        "actor": actor,
        "action": action,
        "target_type": target_type,
        "target_id": target_id,
        "details": json.dumps(details),
    }

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, db_payload)
        conn.commit()


def list_email_samples() -> list[dict]:
    query = """
        SELECT
            id,
            source_type,
            source_name,
            subject,
            from_address,
            from_domain,
            reply_to,
            message_id,
            text_body,
            html_body,
            extracted_links,
            metadata,
            created_at
        FROM email_samples
        ORDER BY id DESC;
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

    items = []
    for row in rows:
        items.append({
            "id": row[0],
            "source_type": row[1],
            "source_name": row[2],
            "subject": row[3],
            "from_address": row[4],
            "from_domain": row[5],
            "reply_to": row[6],
            "message_id": row[7],
            "text_body": row[8],
            "html_body": row[9],
            "extracted_links": row[10] or [],
            "metadata": row[11] or {},
            "created_at": row[12].isoformat() if row[12] else None,
        })

    return items


def get_email_sample_by_id(sample_id: int) -> dict | None:
    query = """
        SELECT
            id,
            source_type,
            source_name,
            subject,
            from_address,
            from_domain,
            reply_to,
            message_id,
            text_body,
            html_body,
            extracted_links,
            metadata,
            created_at
        FROM email_samples
        WHERE id = %(sample_id)s;
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, {"sample_id": sample_id})
            row = cur.fetchone()

    if not row:
        return None

    return {
        "id": row[0],
        "source_type": row[1],
        "source_name": row[2],
        "subject": row[3],
        "from_address": row[4],
        "from_domain": row[5],
        "reply_to": row[6],
        "message_id": row[7],
        "text_body": row[8],
        "html_body": row[9],
        "extracted_links": row[10] or [],
        "metadata": row[11] or {},
        "created_at": row[12].isoformat() if row[12] else None,
    }

def insert_detection(payload: Dict[str, Any]) -> int:
    query = """
        INSERT INTO detections (
            email_sample_id,
            verdict,
            risk_score,
            confidence,
            reasoning_summary,
            detected_signals,
            recommended_action,
            model_versions,
            evidence
        )
        VALUES (
            %(email_sample_id)s,
            %(verdict)s,
            %(risk_score)s,
            %(confidence)s,
            %(reasoning_summary)s,
            %(detected_signals)s::jsonb,
            %(recommended_action)s,
            %(model_versions)s::jsonb,
            %(evidence)s::jsonb
        )
        RETURNING id;
    """

    db_payload = {
        "email_sample_id": payload["email_sample_id"],
        "verdict": payload["verdict"],
        "risk_score": payload["risk_score"],
        "confidence": payload.get("confidence"),
        "reasoning_summary": payload.get("reasoning_summary"),
        "detected_signals": json.dumps(payload.get("detected_signals", [])),
        "recommended_action": payload.get("recommended_action"),
        "model_versions": json.dumps(payload.get("model_versions", {})),
        "evidence": json.dumps(payload.get("evidence", {})),
    }

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, db_payload)
            inserted_id = cur.fetchone()[0]
        conn.commit()

    return inserted_id

def insert_analyst_feedback(payload: Dict[str, Any]) -> int:
    query = """
        INSERT INTO analyst_feedback (
            detection_id,
            analyst_email,
            corrected_verdict,
            notes,
            useful
        )
        VALUES (
            %(detection_id)s,
            %(analyst_email)s,
            %(corrected_verdict)s,
            %(notes)s,
            %(useful)s
        )
        RETURNING id;
    """

    db_payload = {
        "detection_id": payload["detection_id"],
        "analyst_email": payload["analyst_email"],
        "corrected_verdict": payload.get("corrected_verdict"),
        "notes": payload.get("notes"),
        "useful": payload.get("useful"),
    }

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, db_payload)
            inserted_id = cur.fetchone()[0]
        conn.commit()

    return inserted_id

def list_detections() -> list[dict]:
    query = """
        SELECT
            id,
            email_sample_id,
            verdict,
            risk_score,
            confidence,
            reasoning_summary,
            created_at
        FROM detections
        ORDER BY id DESC;
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()

    items = []
    for row in rows:
        items.append({
            "id": row[0],
            "email_sample_id": row[1],
            "verdict": row[2],
            "risk_score": float(row[3]),
            "confidence": float(row[4]) if row[4] is not None else None,
            "reasoning_summary": row[5],
            "created_at": row[6].isoformat() if row[6] else None,
        })

    return items


def get_detection_by_id(detection_id: int) -> dict | None:
    query = """
        SELECT
            id,
            email_sample_id,
            verdict,
            risk_score,
            confidence,
            reasoning_summary,
            detected_signals,
            recommended_action,
            model_versions,
            evidence
        FROM detections
        WHERE id = %(detection_id)s;
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, {"detection_id": detection_id})
            row = cur.fetchone()

    if not row:
        return None

    return {
        "id": row[0],
        "email_sample_id": row[1],
        "verdict": row[2],
        "risk_score": float(row[3]),
        "confidence": float(row[4]) if row[4] is not None else None,
        "reasoning_summary": row[5],
        "detected_signals": row[6] or [],
        "recommended_action": row[7],
        "model_versions": row[8] or {},
        "evidence": row[9] or {},
    }