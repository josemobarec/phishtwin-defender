from typing import Any, Dict

from app.models import ParsedEmail
from app.services.normalizer import (
    extract_domain,
    extract_links_from_text,
    normalize_links,
    safe_strip,
)


def parse_email_json(payload: Dict[str, Any]) -> ParsedEmail:
    subject = safe_strip(payload.get("subject"))
    from_address = safe_strip(payload.get("from_address"))
    reply_to = safe_strip(payload.get("reply_to"))
    message_id = safe_strip(payload.get("message_id"))
    text_body = safe_strip(payload.get("text_body"))
    html_body = safe_strip(payload.get("html_body"))
    headers = payload.get("headers") or {}

    text_links = extract_links_from_text(text_body)
    html_links = extract_links_from_text(html_body)
    extracted_links = normalize_links(text_links + html_links)

    from_domain = extract_domain(from_address)

    reply_to_domain = extract_domain(reply_to)
    reply_to_mismatch = (
        from_domain is not None
        and reply_to_domain is not None
        and from_domain != reply_to_domain
    )

    return ParsedEmail(
        subject=subject,
        from_address=from_address,
        from_domain=from_domain,
        reply_to=reply_to,
        message_id=message_id,
        text_body=text_body,
        html_body=html_body,
        headers=headers,
        extracted_links=extracted_links,
        has_html=html_body is not None,
        has_links=len(extracted_links) > 0,
        reply_to_mismatch=reply_to_mismatch,
        raw_source_type="json",
    )


def parse_email_input(payload: Dict[str, Any]) -> ParsedEmail:
    """
    Punto de entrada del parser.
    En este paso solo manejamos email_json.
    El soporte EML se agrega en el siguiente paso.
    """
    email_json = payload.get("email_json")

    if email_json:
        return parse_email_json(email_json)

    return ParsedEmail(
        subject=None,
        from_address=None,
        from_domain=None,
        reply_to=None,
        message_id=None,
        text_body=None,
        html_body=None,
        headers={},
        extracted_links=[],
        has_html=False,
        has_links=False,
        reply_to_mismatch=False,
        raw_source_type="unknown",
    )