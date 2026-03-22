from typing import Dict, List

from app.models import DetectedSignal


def _clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    return max(min_value, min(max_value, value))


def _compute_confidence(risk_score: float, signal_count: int) -> float:
    """
    Confidence simple para MVP:
    - sube con el risk_score
    - sube ligeramente si hay más de una señal
    """
    base = risk_score * 0.75
    bonus = min(signal_count * 0.05, 0.20)
    return round(_clamp(base + bonus), 2)


def _compute_verdict(risk_score: float) -> str:
    if risk_score >= 0.70:
        return "high-risk"
    if risk_score >= 0.30:
        return "suspicious"
    return "benign"


def calculate_risk_score(signals: List[DetectedSignal]) -> Dict[str, float | str]:
    total_weight = sum(signal.weight for signal in signals)
    risk_score = round(_clamp(total_weight), 2)
    confidence = _compute_confidence(risk_score, len(signals))
    verdict = _compute_verdict(risk_score)

    return {
        "risk_score": risk_score,
        "confidence": confidence,
        "verdict": verdict,
    }