from email import message_from_string, policy
from email.message import EmailMessage
from typing import Any, Dict, Tuple

from app.models import ParsedEmail
from app.services.normalizer import (
    extract_domain,
    extract_links_from_html,
    extract_links_from_text,
    normalize_links,
    safe_strip,
)


def _extract_headers(message: EmailMessage) -> Dict[str, Any]:
    headers: Dict[str, Any] = {}

    for key, value in message.items():
        headers[key] = str(value)

    return headers


def _extract_text_and_html_from_message(message: EmailMessage) -> Tuple[str | None, str | None]:
    text_body = None
    html_body = None

    if message.is_multipart():
        for part in message.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get_content_disposition() or "").lower()

            if content_disposition == "attachment":
                continue

            try:
                content = part.get_content()
            except Exception:
                content = None

            if not content:
                continue

            if content_type == "text/plain" and text_body is None:
                text_body = str(content)
            elif content_type == "text/html" and html_body is None:
                html_body = str(content)
    else:
        content_type = message.get_content_type()

        try:
            content = message.get_content()
        except Exception:
            content = None

        if content:
            if content_type == "text/plain":
                text_body = str(content)
            elif content_type == "text/html":
                html_body = str(content)

    return safe_strip(text_body), safe_strip(html_body)


def _build_parsed_email(
    *,
    subject: str | None,
    from_address: str | None,
    reply_to: str | None,
    message_id: str | None,
    text_body: str | None,
    html_body: str | None,
    headers: Dict[str, Any],
    raw_source_type: str,
) -> ParsedEmail:
    text_links = extract_links_from_text(text_body)
    html_links = extract_links_from_html(html_body)
    extracted_links = normalize_links(text_links + html_links)

    from_domain = extract_domain(from_address)
    reply_to_domain = extract_domain(reply_to)

    reply_to_mismatch = (
        from_domain is not None
        and reply_to_domain is not None
        and from_domain != reply_to_domain
    )

    return ParsedEmail(
        subject=safe_strip(subject),
        from_address=safe_strip(from_address),
        from_domain=from_domain,
        reply_to=safe_strip(reply_to),
        message_id=safe_strip(message_id),
        text_body=text_body,
        html_body=html_body,
        headers=headers,
        extracted_links=extracted_links,
        has_html=html_body is not None,
        has_links=len(extracted_links) > 0,
        reply_to_mismatch=reply_to_mismatch,
        raw_source_type=raw_source_type,
    )


def parse_email_json(payload: Dict[str, Any]) -> ParsedEmail:
    subject = safe_strip(payload.get("subject"))
    from_address = safe_strip(payload.get("from_address"))
    reply_to = safe_strip(payload.get("reply_to"))
    message_id = safe_strip(payload.get("message_id"))
    text_body = safe_strip(payload.get("text_body"))
    html_body = safe_strip(payload.get("html_body"))
    headers = payload.get("headers") or {}

    return _build_parsed_email(
        subject=subject,
        from_address=from_address,
        reply_to=reply_to,
        message_id=message_id,
        text_body=text_body,
        html_body=html_body,
        headers=headers,
        raw_source_type="json",
    )


def parse_email_eml(eml_content: str) -> ParsedEmail:
    message = message_from_string(eml_content, policy=policy.default)

    headers = _extract_headers(message)
    subject = str(message.get("Subject")) if message.get("Subject") else None
    from_address = str(message.get("From")) if message.get("From") else None
    reply_to = str(message.get("Reply-To")) if message.get("Reply-To") else None
    message_id = str(message.get("Message-ID")) if message.get("Message-ID") else None

    text_body, html_body = _extract_text_and_html_from_message(message)

    return _build_parsed_email(
        subject=subject,
        from_address=from_address,
        reply_to=reply_to,
        message_id=message_id,
        text_body=text_body,
        html_body=html_body,
        headers=headers,
        raw_source_type="eml",
    )


def parse_email_input(payload: Dict[str, Any]) -> ParsedEmail:
    email_json = payload.get("email_json")
    eml_content = payload.get("eml_content")

    if email_json:
        return parse_email_json(email_json)

    if eml_content:
        return parse_email_eml(eml_content)

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