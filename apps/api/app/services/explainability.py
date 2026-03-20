from __future__ import annotations

from app.schemas.email import AnalysisResult
from app.services.scoring import ScoreOutput


class ExplainabilityService:
    def build_summary(self, score_output: ScoreOutput) -> str:
        if not score_output.signals:
            return "No se encontraron señales relevantes; el correo parece benigno con la evidencia disponible."

        top_signals = sorted(score_output.signals, key=lambda s: s.weight, reverse=True)[:3]
        bullet_text = "; ".join(signal.description for signal in top_signals)
        return (
            f"El veredicto se basa principalmente en: {bullet_text}. "
            f"La confianza es {score_output.confidence:.2f} y el risk score total es {score_output.risk_score:.2f}."
        )

    def recommend_action(self, verdict: str) -> str:
        mapping = {
            "malicious": "Quarantine, bloquear IOC derivados y escalar al analista SOC.",
            "suspicious": "Enviar a revisión manual y solicitar validación contextual del remitente.",
            "benign": "Permitir con monitoreo pasivo y conservar trazabilidad.",
        }
        return mapping[verdict]

    def build_result(self, score_output: ScoreOutput) -> AnalysisResult:
        return AnalysisResult(
            verdict=score_output.verdict,
            risk_score=score_output.risk_score,
            confidence=score_output.confidence,
            detected_signals=score_output.signals,
            reasoning_summary=self.build_summary(score_output),
            recommended_action=self.recommend_action(score_output.verdict),
            model_versions={
                "ruleset": "rules-v0.1.0",
                "tabular_model": "demo-xgb-v0.1.0",
                "semantic_model": "demo-minilm-v0.1.0",
                "llm_explainer": "disabled",
            },
            evidence=score_output.evidence,
        )
