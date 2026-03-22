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