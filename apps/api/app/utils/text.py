import re
from urllib.parse import urlparse

URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)


def extract_urls(text: str) -> list[str]:
    return list(dict.fromkeys(URL_RE.findall(text or "")))


def get_domain(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip().lower()
    if "@" in value and not value.startswith("http"):
        return value.split("@")[-1]
    try:
        parsed = urlparse(value)
        return parsed.netloc.lower() or None
    except Exception:
        return None


def urgency_score(text: str) -> float:
    tokens = [
        "urgente", "inmediato", "ahora", "asap", "confidencial", "no compartas",
        "transferencia", "pago hoy", "vence hoy", "verify now", "action required",
    ]
    normalized = (text or "").lower()
    hits = sum(1 for token in tokens if token in normalized)
    return min(1.0, hits / 4)


def contains_qr_hint(text: str) -> bool:
    normalized = (text or "").lower()
    return any(token in normalized for token in ["qr", "scan", "escanee", "escanea", "código qr", "code"])
