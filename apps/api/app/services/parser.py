from __future__ import annotations

from email import policy
from email.parser import BytesParser
from typing import Any

from bs4 import BeautifulSoup

from app.schemas.email import AnalyzeEmailRequest, AttachmentMeta, HeaderKV, ParsedEmail
from app.utils.text import extract_urls, get_domain


class EmailParserService:
    def parse(self, payload: AnalyzeEmailRequest) -> ParsedEmail:
        if payload.eml_content:
            return self._parse_eml(payload.eml_content.encode("utf-8", errors="ignore"))
        if payload.email_json:
            return self._parse_json(payload.email_json)
        raise ValueError("Debe enviar eml_content o email_json")

    def _parse_eml(self, eml_bytes: bytes) -> ParsedEmail:
        message = BytesParser(policy=policy.default).parsebytes(eml_bytes)
        text_body = ""
        html_body = ""
        attachments: list[AttachmentMeta] = []

        for part in message.walk():
            content_disposition = part.get_content_disposition()
            content_type = part.get_content_type()

            if content_disposition == "attachment":
                attachments.append(
                    AttachmentMeta(
                        filename=part.get_filename() or "attachment.bin",
                        content_type=content_type,
                        size_bytes=len(part.get_payload(decode=True) or b""),
                        allowed=content_type in {"application/pdf", "text/plain", "image/png", "image/jpeg"},
                    )
                )
                continue

            if content_type == "text/plain" and not text_body:
                text_body = part.get_content() or ""
            elif content_type == "text/html" and not html_body:
                html_body = part.get_content() or ""

        if html_body and not text_body:
            text_body = BeautifulSoup(html_body, "html.parser").get_text(" ", strip=True)

        headers = [HeaderKV(name=k, value=v) for k, v in message.items()]
        links = extract_urls(f"{text_body}\n{html_body}")

        return ParsedEmail(
            subject=message.get("Subject"),
            from_address=message.get("From"),
            from_domain=get_domain(message.get("From")),
            reply_to=message.get("Reply-To"),
            message_id=message.get("Message-ID"),
            text_body=text_body,
            html_body=html_body,
            links=links,
            headers=headers,
            attachments=attachments,
            metadata={
                "header_count": len(headers),
                "has_html": bool(html_body),
                "has_text": bool(text_body),
            },
        )

    def _parse_json(self, data: dict[str, Any]) -> ParsedEmail:
        text_body = data.get("text_body", "")
        html_body = data.get("html_body", "")
        links = data.get("links") or extract_urls(f"{text_body}\n{html_body}")

        attachments = [AttachmentMeta(**item) for item in data.get("attachments", [])]
        headers = [HeaderKV(**item) for item in data.get("headers", [])]

        from_address = data.get("from_address")
        return ParsedEmail(
            subject=data.get("subject"),
            from_address=from_address,
            from_domain=get_domain(from_address),
            reply_to=data.get("reply_to"),
            message_id=data.get("message_id"),
            text_body=text_body,
            html_body=html_body,
            links=links,
            headers=headers,
            qr_values=data.get("qr_values", []),
            attachments=attachments,
            metadata=data.get("metadata", {}),
        )
