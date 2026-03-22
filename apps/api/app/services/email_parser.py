from typing import Any, Dict


def parse_email_input(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Punto de entrada del parser.
    Más adelante decidirá si parsear desde JSON o desde EML.
    """
    return {
        "subject": None,
        "from_address": None,
        "from_domain": None,
        "reply_to": None,
        "message_id": None,
        "text_body": None,
        "html_body": None,
        "headers": {},
        "extracted_links": [],
        "has_html": False,
        "has_links": False,
        "reply_to_mismatch": False,
        "raw_source_type": "unknown"
    }