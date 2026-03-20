from __future__ import annotations

from dataclasses import dataclass

from app.schemas.email import AnalysisEvidence, DetectedSignal, ParsedEmail
from app.utils.text import contains_qr_hint, get_domain, urgency_score


@dataclass
class ScoreOutput:
    verdict: str
    risk_score: float
    confidence: float
    signals: list[DetectedSignal]
    evidence: AnalysisEvidence
    feature_vector: dict


class RiskScoringService:
    SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "cutt.ly", "rebrand.ly"}
    FREE_MAIL = {"gmail.com", "outlook.com", "hotmail.com", "yahoo.com"}

    def analyze(self, parsed: ParsedEmail) -> ScoreOutput:
        signals: list[DetectedSignal] = []
        text = f"{parsed.subject or ''} {parsed.text_body or ''} {parsed.html_body or ''}".strip()
        from_domain = parsed.from_domain or ""
        reply_domain = get_domain(parsed.reply_to)

        feature_vector = {
            "link_count": len(parsed.links),
            "attachment_count": len(parsed.attachments),
            "qr_count": len(parsed.qr_values),
            "urgency_score": urgency_score(text),
            "has_reply_to": bool(parsed.reply_to),
            "from_free_mail": from_domain in self.FREE_MAIL,
            "reply_domain_mismatch": bool(parsed.reply_to and reply_domain and reply_domain != from_domain),
            "has_html": bool(parsed.html_body),
            "header_count": len(parsed.headers),
        }

        if feature_vector["reply_domain_mismatch"]:
            signals.append(self._signal(
                "reply_to_mismatch", "identity", "high", 0.20,
                "El dominio de Reply-To no coincide con el dominio del remitente.",
                {"from_domain": from_domain, "reply_domain": reply_domain},
            ))

        if feature_vector["from_free_mail"]:
            signals.append(self._signal(
                "free_mail_sender", "identity", "medium", 0.10,
                "El remitente usa un proveedor de correo genérico, algo poco común en comunicaciones corporativas sensibles.",
                {"from_domain": from_domain},
            ))

        suspicious_links = []
        for url in parsed.links:
            domain = get_domain(url) or ""
            if domain in self.SHORTENERS:
                suspicious_links.append({"url": url, "reason": "url_shortener"})
                signals.append(self._signal(
                    "shortened_url", "technical", "high", 0.22,
                    "Se detectó un acortador de URL, patrón frecuente en phishing.",
                    {"url": url, "domain": domain},
                ))
            if from_domain and domain and from_domain not in domain:
                suspicious_links.append({"url": url, "reason": "domain_mismatch"})

        urgency = feature_vector["urgency_score"]
        if urgency >= 0.5:
            signals.append(self._signal(
                "urgency_manipulation", "linguistic", "medium", 0.18,
                "El mensaje contiene señales fuertes de urgencia o presión psicológica.",
                {"urgency_score": urgency},
            ))

        if not parsed.links and not parsed.attachments and any(token in text.lower() for token in ["transfer", "wire", "invoice", "gift card", "urgente", "confidencial"]):
            signals.append(self._signal(
                "possible_bec", "semantic", "high", 0.28,
                "El patrón textual es compatible con BEC sin malware ni enlaces.",
                {"link_count": len(parsed.links), "attachment_count": len(parsed.attachments)},
                source="ml",
            ))

        if parsed.qr_values or contains_qr_hint(text):
            signals.append(self._signal(
                "qr_presence", "visual", "high", 0.25,
                "Se detecta presencia o referencia a código QR; requiere verificación del destino real.",
                {"qr_values": parsed.qr_values},
            ))

        if parsed.subject and any(token in parsed.subject.lower() for token in ["account", "password", "verify", "invoice", "payment"]):
            signals.append(self._signal(
                "credential_or_finance_theme", "semantic", "medium", 0.12,
                "El asunto usa un tema frecuente en campañas de phishing o fraude financiero.",
                {"subject": parsed.subject},
                source="ml",
            ))

        score = round(min(0.99, sum(signal.weight for signal in signals)), 2)
        confidence = round(min(0.98, 0.55 + (len(signals) * 0.07)), 2)

        if score >= 0.75:
            verdict = "malicious"
        elif score >= 0.45:
            verdict = "suspicious"
        else:
            verdict = "benign"

        evidence = AnalysisEvidence(
            headers={
                "from_address": parsed.from_address,
                "from_domain": from_domain,
                "reply_to": parsed.reply_to,
                "header_count": len(parsed.headers),
            },
            links=suspicious_links,
            linguistic={"urgency_score": urgency},
            brand={},
            visual={"qr_values": parsed.qr_values, "html_present": bool(parsed.html_body)},
        )

        return ScoreOutput(
            verdict=verdict,
            risk_score=score,
            confidence=confidence,
            signals=signals,
            evidence=evidence,
            feature_vector=feature_vector,
        )

    def _signal(self, signal_id: str, category: str, severity: str, weight: float, description: str, evidence: dict, source: str = "rule") -> DetectedSignal:
        return DetectedSignal(
            signal_id=signal_id,
            category=category,
            severity=severity,
            weight=weight,
            description=description,
            evidence=evidence,
            source=source,
        )
