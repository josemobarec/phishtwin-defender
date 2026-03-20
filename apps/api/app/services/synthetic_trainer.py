from __future__ import annotations

from app.schemas.email import SyntheticGenerateRequest


class SyntheticTrainerService:
    SAFE_DOMAINS = ["training.invalid", "example.invalid", "awareness.local"]

    def generate(self, request: SyntheticGenerateRequest) -> list[dict]:
        samples = []
        for idx in range(request.count):
            samples.append(
                {
                    "title": f"Simulación segura {request.scenario_type} #{idx + 1}",
                    "scenario_type": request.scenario_type,
                    "language": request.language,
                    "sophistication": request.sophistication,
                    "tone": request.tone,
                    "subject": self._subject(request),
                    "body": self._body(request),
                    "labels": [request.scenario_type, "synthetic", "safe-training"],
                    "pedagogical_reasons": [
                        "Practicar detección de urgencia y suplantación contextual.",
                        "No contiene enlaces activos ni credenciales reales.",
                        "Incluye señales explicables para capacitación interna.",
                    ],
                    "safe_artifacts": {
                        "links": [f"https://{self.SAFE_DOMAINS[idx % len(self.SAFE_DOMAINS)]}/awareness/{request.scenario_type}"],
                        "credentials": ["<redacted-demo-only>"],
                        "brand_style": "genérico / ficticio",
                    },
                }
            )
        return samples

    def _subject(self, request: SyntheticGenerateRequest) -> str:
        mapping = {
            "invoice_bec": "Revisión interna de factura pendiente — ejercicio de concienciación",
            "qr_alert": "Actualización de acceso con QR — simulación segura",
            "login_notice": "Verificación de cuenta corporativa — entrenamiento interno",
            "exec_request": "Solicitud ejecutiva extraordinaria — ejercicio controlado",
            "hr_update": "Actualización de RR.HH. — campaña educativa",
        }
        return mapping.get(request.scenario_type, "Simulación interna de seguridad")

    def _body(self, request: SyntheticGenerateRequest) -> str:
        return (
            f"Este es un ejemplo sintético y seguro orientado a {request.audience}. "
            f"Se diseñó con tono {request.tone} y nivel {request.sophistication}. "
            "No requiere acciones reales, no usa marcas reales y todos los artefactos son inofensivos. "
            "Objetivo pedagógico: identificar presión temporal, señales de identidad dudosa y consistencia del mensaje."
        )
