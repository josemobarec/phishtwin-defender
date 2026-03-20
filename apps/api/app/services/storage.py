from __future__ import annotations

from sqlmodel import Session, select

from app.models.entities import AnalystFeedback, AuditLog, BrandProfile, Detection, EmailSample, SyntheticSample
from app.schemas.email import AnalysisResult, BrandProfileRequest, FeedbackRequest, ParsedEmail
from app.services.scoring import ScoreOutput


class PersistenceService:
    def save_email_and_detection(self, session: Session, parsed: ParsedEmail, result: AnalysisResult, score_output: ScoreOutput, source_name: str | None = None) -> Detection:
        email_sample = EmailSample(
            source_type="upload",
            source_name=source_name,
            subject=parsed.subject,
            from_address=parsed.from_address,
            from_domain=parsed.from_domain,
            reply_to=parsed.reply_to,
            message_id=parsed.message_id,
            text_body=parsed.text_body,
            html_body=parsed.html_body,
            qr_values=parsed.qr_values,
            attachments=[attachment.model_dump() for attachment in parsed.attachments],
            metadata=parsed.metadata,
        )
        session.add(email_sample)
        session.commit()
        session.refresh(email_sample)

        detection = Detection(
            email_sample_id=email_sample.id,
            verdict=result.verdict,
            risk_score=result.risk_score,
            confidence=result.confidence,
            recommended_action=result.recommended_action,
            detected_signals=[signal.model_dump() for signal in result.detected_signals],
            reasoning_summary=result.reasoning_summary,
            evidence=result.evidence.model_dump(),
            model_versions=result.model_versions,
            raw_feature_vector=score_output.feature_vector,
        )
        session.add(detection)
        session.commit()
        session.refresh(detection)

        self._audit(session, actor="system", action="analyze_email", target_type="detection", target_id=str(detection.id), details={"verdict": detection.verdict})
        return detection

    def save_feedback(self, session: Session, payload: FeedbackRequest) -> AnalystFeedback:
        feedback = AnalystFeedback(**payload.model_dump())
        session.add(feedback)
        session.commit()
        session.refresh(feedback)
        self._audit(session, actor=payload.analyst_email, action="submit_feedback", target_type="detection", target_id=str(payload.detection_id), details={"corrected_verdict": payload.corrected_verdict})
        return feedback

    def save_synthetic_samples(self, session: Session, samples: list[dict]) -> list[SyntheticSample]:
        stored = []
        for sample in samples:
            row = SyntheticSample(
                title=sample["title"],
                scenario_type=sample["scenario_type"],
                language=sample["language"],
                sophistication=sample["sophistication"],
                tone=sample["tone"],
                content={"subject": sample["subject"], "body": sample["body"], "safe_artifacts": sample["safe_artifacts"]},
                pedagogy={"labels": sample["labels"], "reasons": sample["pedagogical_reasons"]},
            )
            session.add(row)
            stored.append(row)
        session.commit()
        return stored

    def save_brand(self, session: Session, payload: BrandProfileRequest) -> BrandProfile:
        brand = BrandProfile(**payload.model_dump())
        session.add(brand)
        session.commit()
        session.refresh(brand)
        self._audit(session, actor="system", action="create_brand_profile", target_type="brand_profile", target_id=str(brand.id), details={"name": brand.name})
        return brand

    def list_detections(self, session: Session) -> list[Detection]:
        return list(session.exec(select(Detection).order_by(Detection.created_at.desc())).all())

    def get_detection(self, session: Session, detection_id: int) -> Detection | None:
        return session.get(Detection, detection_id)

    def _audit(self, session: Session, actor: str, action: str, target_type: str, target_id: str, details: dict) -> None:
        session.add(AuditLog(actor=actor, action=action, target_type=target_type, target_id=target_id, details=details))
        session.commit()
