from typing import Any, Dict, List


def build_detection_explanation(
    parsed_email: Dict[str, Any],
    signals: List[Dict[str, Any]],
    score_result: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Construye una explicación básica del resultado de detección.
    En este paso dejamos el esqueleto base.
    """
    return {
        "reasoning_summary": "Initial detection pipeline created. Rule-based explanation pending.",
        "recommended_action": "Review manually if needed.",
        "evidence": {
            "from_domain": parsed_email.get("from_domain"),
            "reply_to": parsed_email.get("reply_to"),
            "has_links": parsed_email.get("has_links"),
            "has_html": parsed_email.get("has_html"),
            "reply_to_mismatch": parsed_email.get("reply_to_mismatch"),
            "extracted_links": parsed_email.get("extracted_links", []),
        }
    }