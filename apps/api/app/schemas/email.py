from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class HeaderKV(BaseModel):
    name: str
    value: str


class AttachmentMeta(BaseModel):
    filename: str
    content_type: str
    size_bytes: int = 0
    sha256: Optional[str] = None
    allowed: bool = True


class AnalyzeEmailRequest(BaseModel):
    eml_content: Optional[str] = Field(default=None, description="Contenido EML como texto completo")
    email_json: Optional[dict[str, Any]] = Field(default=None, description="Representación JSON segura del correo")
    source_name: Optional[str] = None
    analyst_context: Optional[dict[str, Any]] = None


class ParsedEmail(BaseModel):
    subject: Optional[str] = None
    from_address: Optional[str] = None
    from_domain: Optional[str] = None
    reply_to: Optional[str] = None
    message_id: Optional[str] = None
    received_at: Optional[datetime] = None
    text_body: str = ""
    html_body: str = ""
    links: list[str] = Field(default_factory=list)
    headers: list[HeaderKV] = Field(default_factory=list)
    qr_values: list[str] = Field(default_factory=list)
    attachments: list[AttachmentMeta] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DetectedSignal(BaseModel):
    signal_id: str
    category: str
    severity: str
    weight: float
    description: str
    evidence: dict[str, Any] = Field(default_factory=dict)
    source: str = Field(default="rule")


class AnalysisEvidence(BaseModel):
    headers: dict[str, Any] = Field(default_factory=dict)
    links: list[dict[str, Any]] = Field(default_factory=list)
    linguistic: dict[str, Any] = Field(default_factory=dict)
    brand: dict[str, Any] = Field(default_factory=dict)
    visual: dict[str, Any] = Field(default_factory=dict)


class AnalysisResult(BaseModel):
    detection_id: Optional[int] = None
    verdict: str
    risk_score: float
    confidence: float
    detected_signals: list[DetectedSignal]
    reasoning_summary: str
    recommended_action: str
    analyst_notes: Optional[str] = None
    model_versions: dict[str, str]
    evidence: AnalysisEvidence


class DetectionSummary(BaseModel):
    id: int
    verdict: str
    risk_score: float
    confidence: float
    subject: Optional[str] = None
    from_address: Optional[str] = None
    created_at: datetime


class FeedbackRequest(BaseModel):
    detection_id: int
    analyst_email: str
    corrected_verdict: str
    notes: Optional[str] = None
    useful: bool = True


class ScreenshotAnalysisRequest(BaseModel):
    screenshot_b64: str
    claimed_brand: Optional[str] = None
    visible_domain: Optional[str] = None


class BrandProfileRequest(BaseModel):
    name: str
    official_domains: list[str]
    keywords: list[str] = Field(default_factory=list)
    logo_hashes: list[str] = Field(default_factory=list)


class SyntheticGenerateRequest(BaseModel):
    scenario_type: str = Field(description="invoice_bec, qr_alert, login_notice, exec_request, hr_update")
    language: str = "es"
    sophistication: str = "medium"
    tone: str = "urgent"
    audience: str = "employees"
    count: int = 1


class SyntheticGenerateResponse(BaseModel):
    samples: list[dict[str, Any]]
