from typing import Any, Dict, List


def evaluate_detection_rules(parsed_email: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Evalúa reglas simples sobre el correo parseado y devuelve
    una lista de señales detectadas.
    En este paso dejamos solo el esqueleto base.
    """
    signals: List[Dict[str, Any]] = []

    return signals