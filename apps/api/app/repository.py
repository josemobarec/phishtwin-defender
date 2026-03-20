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