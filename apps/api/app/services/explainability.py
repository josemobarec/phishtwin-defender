from typing import Any, Dict, List

from app.models import DetectedSignal


def _sort_signals(signals: List[DetectedSignal]) -> List[DetectedSignal]:
    severity_rank = {
        "high": 3,
        "medium": 2,
        "low": 1,
    }

    return sorted(
        signals,
        key=lambda s: (severity_rank.get(s.severity, 0), s.weight),
        reverse=True,
    )


def _top_signal_descriptions(signals: List[DetectedSignal], limit: int = 3) -> List[str]:
    ordered = _sort_signals(signals)
    return [signal.description for signal in ordered[:limit]]


def _signal_categories(signals: List[DetectedSignal]) -> List[str]:
    seen = []
    for signal in signals:
        if signal.category not in seen:
            seen.append(signal.category)
    return seen


def _build_reasoning_summary(
    verdict: str,
    signals: List[DetectedSignal],
    risk_score: float,
) -> str:
    if not signals:
        return (
            f"No se detectaron señales relevantes con el ruleset actual. "
            f"El correo fue clasificado como {verdict} con risk score {risk_score:.2f}."
        )

    top_descriptions = _top_signal_descriptions(signals, limit=3)
    categories = _signal_categories(signals)

    if verdict == "high-risk":
        prefix = (
            f"El correo fue clasificado como high-risk con risk score {risk_score:.2f} "
            f"porque combina múltiples señales fuertes de riesgo"
        )
    elif verdict == "suspicious":
        prefix = (
            f"El correo fue clasificado como suspicious con risk score {risk_score:.2f} "
            f"porque presenta señales compatibles con fraude, suplantación o ingeniería social"
        )
    else:
        prefix = (
            f"El correo fue clasificado como benign con risk score {risk_score:.2f}, "
            f"aunque se detectaron señales menores"
        )

    category_text = ""
    if categories:
        category_text = f" en las categorías {', '.join(categories[:3])}"

    return f"{prefix}{category_text}: " + "; ".join(top_descriptions) + "."


def _build_recommended_action(verdict: str, signals: List[DetectedSignal]) -> str:
    signal_ids = {signal.signal_id for signal in signals}

    if verdict == "high-risk":
        return (
            "Retener para revisión manual inmediata, validar por canal alterno con el supuesto remitente "
            "y evitar cualquier acción financiera, de credenciales o apertura de enlaces hasta confirmar legitimidad."
        )

    if verdict == "suspicious":
        if (
            "financial_language" in signal_ids
            or "reply_to_mismatch" in signal_ids
            or "sender_link_domain_mismatch" in signal_ids
        ):
            return (
                "Revisar manualmente antes de actuar, verificar remitente, dominio y enlaces, "
                "y validar por canal alterno cualquier solicitud sensible."
            )

        return (
            "Revisar manualmente el mensaje y confirmar si el contexto, remitente y enlaces son coherentes "
            "antes de continuar."
        )

    return (
        "No se requieren acciones inmediatas con el ruleset actual, "
        "aunque el correo puede revisarse manualmente si el contexto del negocio lo requiere."
    )


def _build_evidence(
    parsed_email: Dict[str, Any],
    signals: List[DetectedSignal],
    score_result: Dict[str, Any],
) -> Dict[str, Any]:
    ordered = _sort_signals(signals)

    return {
        "from_address": parsed_email.get("from_address"),
        "from_domain": parsed_email.get("from_domain"),
        "reply_to": parsed_email.get("reply_to"),
        "subject": parsed_email.get("subject"),
        "has_links": parsed_email.get("has_links"),
        "has_html": parsed_email.get("has_html"),
        "reply_to_mismatch": parsed_email.get("reply_to_mismatch"),
        "extracted_links": parsed_email.get("extracted_links", []),
        "signal_ids": [signal.signal_id for signal in ordered],
        "signal_count": len(signals),
        "top_signals": [signal.model_dump() for signal in ordered[:3]],
        "risk_score": score_result.get("risk_score"),
        "confidence": score_result.get("confidence"),
        "verdict": score_result.get("verdict"),
    }


def build_detection_explanation(
    parsed_email: Dict[str, Any],
    signals: List[DetectedSignal],
    score_result: Dict[str, Any],
) -> Dict[str, Any]:
    verdict = score_result["verdict"]
    risk_score = float(score_result["risk_score"])

    reasoning_summary = _build_reasoning_summary(
        verdict=verdict,
        signals=signals,
        risk_score=risk_score,
    )
    recommended_action = _build_recommended_action(verdict, signals)
    evidence = _build_evidence(parsed_email, signals, score_result)

    return {
        "reasoning_summary": reasoning_summary,
        "recommended_action": recommended_action,
        "evidence": evidence,
    }