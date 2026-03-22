from typing import Any, Dict, List


def calculate_risk_score(signals: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calcula un risk score inicial a partir de señales detectadas.
    En este paso dejamos el esqueleto base.
    """
    return {
        "risk_score": 0.0,
        "confidence": 0.0,
        "verdict": "benign"
    }