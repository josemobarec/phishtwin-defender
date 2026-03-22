from typing import Any, Dict, List

from app.models import DetectedSignal


def _build_reasoning_summary(
    verdict: str,
    signals: List[DetectedSignal],
) -> str:
    if not signals:
        return (
            "No se detectaron señales relevantes con el ruleset actual. "
            "El correo fue clasificado con bajo riesgo en esta etapa inicial."
        )

    signal_descriptions = [signal.description for signal in signals[:3]]

    if verdict == "high-risk":
        prefix = "El correo fue clasificado como high-risk porque presenta múltiples señales fuertes"
    elif verdict == "suspicious":
        prefix = "El correo fue clasificado como suspicious porque presenta señales compatibles con fraude o suplantación"
    else:
        prefix = "El correo fue clasificado como benign, aunque se detectaron señales menores"

    return f"{prefix}: " + "; ".join(signal_descriptions) + "."


def _build_recommended_action(verdict: str) -> str:
    if verdict == "high-risk":
        return (
            "Retener para revisión manual, validar por canal alterno con el remitente "
            "y evitar cualquier acción financiera o de credenciales hasta confirmar legitimidad."
        )
    if verdict == "suspicious":
        return (
            "Revisar manualmente antes de actuar, verificar remitente, dominio y enlaces, "
            "y escalar al equipo de seguridad si el contexto es sensible."
        )
    return (
        "No se requieren acciones inmediatas con el ruleset actual, "
        "aunque el correo puede revisarse manualmente si el contexto lo justifica."
    )


def _build_evidence(
    parsed_email: Dict[str, Any],
    signals: List[DetectedSignal],
) -> Dict[str, Any]:
    return {
        "from_address": parsed_email.get("from_address"),
        "from_domain": parsed_email.get("from_domain"),
        "reply_to": parsed_email.get("reply_to"),
        "subject": parsed_email.get("subject"),
        "has_links": parsed_email.get("has_links"),
        "has_html": parsed_email.get("has_html"),
        "reply_to_mismatch": parsed_email.get("reply_to_mismatch"),
        "extracted_links": parsed_email.get("extracted_links", []),
        "signal_ids": [signal.signal_id for signal in signals],
        "signal_count": len(signals),
    }


def build_detection_explanation(
    parsed_email: Dict[str, Any],
    signals: List[DetectedSignal],
    score_result: Dict[str, Any],
) -> Dict[str, Any]:
    verdict = score_result["verdict"]

    reasoning_summary = _build_reasoning_summary(verdict, signals)
    recommended_action = _build_recommended_action(verdict)
    evidence = _build_evidence(parsed_email, signals)

    return {
        "reasoning_summary": reasoning_summary,
        "recommended_action": recommended_action,
        "evidence": evidence,
    }