from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.session import get_session
from app.schemas.email import (
    AnalysisResult,
    AnalyzeEmailRequest,
    BrandProfileRequest,
    FeedbackRequest,
    ScreenshotAnalysisRequest,
    SyntheticGenerateRequest,
    SyntheticGenerateResponse,
)
from app.services.explainability import ExplainabilityService
from app.services.parser import EmailParserService
from app.services.persistence import PersistenceService
from app.services.scoring import RiskScoringService
from app.services.synthetic_trainer import SyntheticTrainerService
from app.services.vision import VisionAnalysisService

router = APIRouter()
parser_service = EmailParserService()
scoring_service = RiskScoringService()
explainer = ExplainabilityService()
persistence = PersistenceService()
synthetic_service = SyntheticTrainerService()
vision_service = VisionAnalysisService()


@router.post("/analyze-email", response_model=AnalysisResult)
def analyze_email(payload: AnalyzeEmailRequest, session: Session = Depends(get_session)):
    parsed = parser_service.parse(payload)
    score_output = scoring_service.analyze(parsed)
    result = explainer.build_result(score_output)
    detection = persistence.save_email_and_detection(session, parsed, result, score_output, payload.source_name)
    result.detection_id = detection.id
    return result


@router.post("/analyze-screenshot")
def analyze_screenshot(payload: ScreenshotAnalysisRequest):
    return vision_service.analyze(payload)


@router.get("/detections")
def get_detections(session: Session = Depends(get_session)):
    rows = persistence.list_detections(session)
    return [
        {
            "id": row.id,
            "verdict": row.verdict,
            "risk_score": row.risk_score,
            "confidence": row.confidence,
            "recommended_action": row.recommended_action,
            "created_at": row.created_at,
        }
        for row in rows
    ]


@router.get("/detections/{detection_id}")
def get_detection(detection_id: int, session: Session = Depends(get_session)):
    row = persistence.get_detection(session, detection_id)
    if not row:
        raise HTTPException(status_code=404, detail="Detection not found")
    return row


@router.post("/feedback")
def post_feedback(payload: FeedbackRequest, session: Session = Depends(get_session)):
    feedback = persistence.save_feedback(session, payload)
    return {"status": "stored", "feedback_id": feedback.id}


@router.post("/synthetic/generate", response_model=SyntheticGenerateResponse)
def generate_synthetic(payload: SyntheticGenerateRequest, session: Session = Depends(get_session)):
    samples = synthetic_service.generate(payload)
    persistence.save_synthetic_samples(session, samples)
    return SyntheticGenerateResponse(samples=samples)


@router.post("/brands")
def create_brand(payload: BrandProfileRequest, session: Session = Depends(get_session)):
    brand = persistence.save_brand(session, payload)
    return {"id": brand.id, "name": brand.name, "official_domains": brand.official_domains}


@router.get("/dashboard/summary")
def dashboard_summary(session: Session = Depends(get_session)):
    rows = persistence.list_detections(session)
    total = len(rows)
    high_risk = len([row for row in rows if row.risk_score >= 0.75])
    suspicious = len([row for row in rows if 0.45 <= row.risk_score < 0.75])
    benign = len([row for row in rows if row.risk_score < 0.45])
    return {
        "totals": {"total": total, "high_risk": high_risk, "suspicious": suspicious, "benign": benign},
        "recent": [
            {"id": row.id, "verdict": row.verdict, "risk_score": row.risk_score, "created_at": row.created_at}
            for row in rows[:10]
        ],
    }
