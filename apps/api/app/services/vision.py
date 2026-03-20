from __future__ import annotations

from app.schemas.email import ScreenshotAnalysisRequest


class VisionAnalysisService:
    def analyze(self, payload: ScreenshotAnalysisRequest) -> dict:
        suspicious = []
        if payload.claimed_brand and payload.visible_domain and payload.claimed_brand.lower() not in payload.visible_domain.lower():
            suspicious.append({
                "signal_id": "brand_domain_misalignment",
                "description": "La marca reclamada no coincide con el dominio visible proporcionado.",
                "severity": "high",
            })

        return {
            "verdict": "suspicious" if suspicious else "unknown",
            "visual_signals": suspicious,
            "notes": [
                "MVP visual: placeholder defensivo para comparación de branding y QR.",
                "En una fase posterior se pueden añadir embeddings visuales y OCR opcional en entorno aislado.",
            ],
        }
