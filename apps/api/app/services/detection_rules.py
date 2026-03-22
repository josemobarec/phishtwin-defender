import re
from typing import Any, Dict, List

from app.models import DetectedSignal
from app.services.normalizer import extract_url_domain, get_base_domain

URGENT_TERMS = [
    "urgent",
    "immediately",
    "asap",
    "today",
    "right away",
    "confidential",
    "do not call",
    "priority",
    "importante",
    "urgente",
    "hoy",
    "confidencial",
]

FINANCIAL_TERMS = [
    "payment",
    "invoice",
    "bank transfer",
    "wire transfer",
    "account details",
    "payroll",
    "factura",
    "pago",
    "transferencia",
    "datos bancarios",
]

FREE_MAIL_DOMAINS = {
    "gmail.com",
    "outlook.com",
    "hotmail.com",
    "yahoo.com",
    "proton.me",
    "protonmail.com",
    "icloud.com",
}

SUSPICIOUS_DOMAIN_PATTERNS = [
    r"\.invalid$",
    r"secure-login",
    r"verify-account",
    r"update-account",
    r"login-secure",
]


def _combine_text(parsed_email: Dict[str, Any]) -> str:
    parts = [
        parsed_email.get("subject") or "",
        parsed_email.get("text_body") or "",
        parsed_email.get("html_body") or "",
    ]
    return " ".join(parts).lower()


def _match_any_term(text: str, terms: List[str]) -> List[str]:
    found = []
    for term in terms:
        if term.lower() in text:
            found.append(term)
    return found


def _domain_matches_suspicious_pattern(domain: str | None) -> List[str]:
    if not domain:
        return []

    matches = []
    for pattern in SUSPICIOUS_DOMAIN_PATTERNS:
        if re.search(pattern, domain, re.IGNORECASE):
            matches.append(pattern)
    return matches


def _extract_link_domains(links: List[str]) -> List[str]:
    domains = []
    seen = set()

    for link in links:
        domain = extract_url_domain(link)
        if domain and domain not in seen:
            seen.add(domain)
            domains.append(domain)

    return domains


def evaluate_detection_rules(parsed_email: Dict[str, Any]) -> List[DetectedSignal]:
    signals: List[DetectedSignal] = []

    subject = parsed_email.get("subject")
    from_address = parsed_email.get("from_address")
    from_domain = parsed_email.get("from_domain")
    reply_to = parsed_email.get("reply_to")
    extracted_links = parsed_email.get("extracted_links", [])
    link_domains = _extract_link_domains(extracted_links)
    from_base_domain = get_base_domain(from_domain)
    has_html = parsed_email.get("has_html", False)
    reply_to_mismatch = parsed_email.get("reply_to_mismatch", False)

    combined_text = _combine_text(parsed_email)

    if reply_to_mismatch:
        signals.append(
            DetectedSignal(
                signal_id="reply_to_mismatch",
                category="identity",
                severity="high",
                weight=0.25,
                description="El dominio de Reply-To no coincide con el dominio del remitente.",
                evidence={
                    "from_domain": from_domain,
                    "reply_to": reply_to,
                },
            )
        )

    if len(extracted_links) > 0:
        signals.append(
            DetectedSignal(
                signal_id="has_links",
                category="technical",
                severity="medium",
                weight=0.10,
                description="El correo contiene uno o más enlaces.",
                evidence={
                    "link_count": len(extracted_links),
                    "links": extracted_links,
                },
            )
        )

    if len(extracted_links) >= 2:
        signals.append(
            DetectedSignal(
                signal_id="multiple_links",
                category="technical",
                severity="medium",
                weight=0.10,
                description="El correo contiene múltiples enlaces, lo que puede aumentar el riesgo.",
                evidence={
                    "link_count": len(extracted_links),
                },
            )
        )

    if has_html:
        signals.append(
            DetectedSignal(
                signal_id="html_present",
                category="technical",
                severity="low",
                weight=0.05,
                description="El correo contiene contenido HTML renderizable.",
                evidence={
                    "has_html": has_html,
                },
            )
        )

    urgent_matches = _match_any_term(combined_text, URGENT_TERMS)
    if urgent_matches:
        signals.append(
            DetectedSignal(
                signal_id="urgency_language",
                category="linguistic",
                severity="medium",
                weight=0.15,
                description="Se detectó lenguaje de urgencia o presión temporal.",
                evidence={
                    "matched_terms": urgent_matches,
                },
            )
        )

    financial_matches = _match_any_term(combined_text, FINANCIAL_TERMS)
    if financial_matches:
        signals.append(
            DetectedSignal(
                signal_id="financial_language",
                category="semantic",
                severity="high",
                weight=0.20,
                description="Se detectó lenguaje relacionado con pagos o solicitudes financieras.",
                evidence={
                    "matched_terms": financial_matches,
                },
            )
        )

    suspicious_domain_matches = _domain_matches_suspicious_pattern(from_domain)
    if suspicious_domain_matches:
        signals.append(
            DetectedSignal(
                signal_id="suspicious_domain_pattern",
                category="identity",
                severity="high",
                weight=0.20,
                description="El dominio del remitente coincide con patrones sospechosos.",
                evidence={
                    "from_domain": from_domain,
                    "matched_patterns": suspicious_domain_matches,
                },
            )
        )

    if from_domain in FREE_MAIL_DOMAINS:
        signals.append(
            DetectedSignal(
                signal_id="external_free_mail_sender",
                category="identity",
                severity="medium",
                weight=0.15,
                description="El remitente utiliza un dominio de correo gratuito.",
                evidence={
                    "from_domain": from_domain,
                    "from_address": from_address,
                },
            )
        )

    suspicious_link_matches = []
    for link_domain in link_domains:
        matches = _domain_matches_suspicious_pattern(link_domain)
        if matches:
            suspicious_link_matches.append({
                "link_domain": link_domain,
                "matched_patterns": matches,
            })

    if suspicious_link_matches:
        signals.append(
            DetectedSignal(
                signal_id="suspicious_link_domain",
                category="technical",
                severity="high",
                weight=0.25,
                description="Uno o más enlaces apuntan a dominios con patrones sospechosos.",
                evidence={
                    "matches": suspicious_link_matches,
                },
            )
        )

    mismatched_link_domains = []
    for link_domain in link_domains:
        link_base_domain = get_base_domain(link_domain)

        if (
            from_base_domain is not None
            and link_base_domain is not None
            and link_base_domain != from_base_domain
        ):
            mismatched_link_domains.append(link_domain)

    if mismatched_link_domains:
        signals.append(
            DetectedSignal(
                signal_id="sender_link_domain_mismatch",
                category="identity",
                severity="high",
                weight=0.20,
                description="El dominio del remitente no coincide con el dominio de destino de uno o más enlaces.",
                evidence={
                    "from_domain": from_domain,
                    "from_base_domain": from_base_domain,
                    "mismatched_link_domains": mismatched_link_domains,
                },
            )
        )

    return signals