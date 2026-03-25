from typing import Dict, List

from app.models import DetectedSignal


def _clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    return max(min_value, min(max_value, value))


def _signal_ids(signals: List[DetectedSignal]) -> set[str]:
    return {signal.signal_id for signal in signals}


def _severity_bonus(signals: List[DetectedSignal]) -> float:
    high_count = sum(1 for signal in signals if signal.severity == "high")
    medium_count = sum(1 for signal in signals if signal.severity == "medium")

    bonus = 0.0

    if high_count >= 2:
        bonus += 0.05
    elif high_count == 1 and medium_count >= 2:
        bonus += 0.03

    return bonus


def _combo_bonus(signal_ids: set[str]) -> float:
    bonus = 0.0

    # BEC-like combo
    if "reply_to_mismatch" in signal_ids and "financial_language" in signal_ids:
        bonus += 0.05

    # Link fraud combo
    if "suspicious_link_domain" in signal_ids and "sender_link_domain_mismatch" in signal_ids:
        bonus += 0.05

    # Urgency + financial language together is slightly stronger
    if "urgency_language" in signal_ids and "financial_language" in signal_ids:
        bonus += 0.03

    return bonus


def _compute_confidence(
    risk_score: float,
    signals: List[DetectedSignal],
    combo_bonus: float,
) -> float:
    signal_count = len(signals)
    categories = {signal.category for signal in signals}
    high_count = sum(1 for signal in signals if signal.severity == "high")

    confidence = risk_score * 0.65
    confidence += min(signal_count * 0.04, 0.16)
    confidence += min(len(categories) * 0.03, 0.12)
    confidence += min(high_count * 0.03, 0.09)
    confidence += combo_bonus * 0.5

    return round(_clamp(confidence), 2)


def _compute_verdict(risk_score: float) -> str:
    if risk_score >= 0.75:
        return "high-risk"
    if risk_score >= 0.25:
        return "suspicious"
    return "benign"


def calculate_risk_score(signals: List[DetectedSignal]) -> Dict[str, float | str]:
    base_score = sum(signal.weight for signal in signals)
    signal_ids = _signal_ids(signals)

    severity_bonus = _severity_bonus(signals)
    combo_bonus = _combo_bonus(signal_ids)

    risk_score = round(_clamp(base_score + severity_bonus + combo_bonus), 2)
    confidence = _compute_confidence(risk_score, signals, combo_bonus)
    verdict = _compute_verdict(risk_score)

    return {
        "risk_score": risk_score,
        "confidence": confidence,
        "verdict": verdict,
    }