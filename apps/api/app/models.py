from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EmailSampleCreate(BaseModel):
    source_type: str = "json"
    source_name: Optional[str] = None
    subject: Optional[str] = None
    from_address: Optional[str] = None
    from_domain: Optional[str] = None
    reply_to: Optional[str] = None
    message_id: Optional[str] = None
    text_body: Optional[str] = None
    html_body: Optional[str] = None
    extracted_links: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EmailSampleResponse(BaseModel):
    id: int
    message: str


class EmailJsonInput(BaseModel):
    subject: Optional[str] = None
    from_address: Optional[str] = None
    reply_to: Optional[str] = None
    message_id: Optional[str] = None
    text_body: Optional[str] = None
    html_body: Optional[str] = None
    headers: Dict[str, Any] = Field(default_factory=dict)


class AnalyzeEmailRequest(BaseModel):
    source_name: Optional[str] = None
    eml_content: Optional[str] = None
    email_json: Optional[EmailJsonInput] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ParsedEmail(BaseModel):
    subject: Optional[str] = None
    from_address: Optional[str] = None
    from_domain: Optional[str] = None
    reply_to: Optional[str] = None
    message_id: Optional[str] = None
    text_body: Optional[str] = None
    html_body: Optional[str] = None
    headers: Dict[str, Any] = Field(default_factory=dict)
    extracted_links: List[str] = Field(default_factory=list)
    has_html: bool = False
    has_links: bool = False
    reply_to_mismatch: bool = False
    raw_source_type: str = "unknown"


class AnalyzeEmailResponse(BaseModel):
    sample_id: int
    parsed_email: ParsedEmail
    message: str = "Email analyzed and stored successfully"

class EmailSampleRecord(BaseModel):
    id: int
    source_type: str
    source_name: Optional[str] = None
    subject: Optional[str] = None
    from_address: Optional[str] = None
    from_domain: Optional[str] = None
    reply_to: Optional[str] = None
    message_id: Optional[str] = None
    text_body: Optional[str] = None
    html_body: Optional[str] = None
    extracted_links: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: str


class EmailSampleListResponse(BaseModel):
    items: List[EmailSampleRecord]
    total: int

class DetectedSignal(BaseModel):
    signal_id: str
    category: str
    severity: str
    weight: float
    description: str
    evidence: Dict[str, Any] = Field(default_factory=dict)

class DetectionRecord(BaseModel):
    id: int
    email_sample_id: int
    verdict: str
    risk_score: float
    confidence: Optional[float] = None
    reasoning_summary: Optional[str] = None
    detected_signals: List[DetectedSignal] = Field(default_factory=list)
    recommended_action: Optional[str] = None
    model_versions: Dict[str, Any] = Field(default_factory=dict)
    evidence: Dict[str, Any] = Field(default_factory=dict)


class AnalyzeEmailResponse(BaseModel):
    sample_id: int
    detection_id: int
    parsed_email: ParsedEmail
    detection: DetectionRecord
    message: str = "Email analyzed and stored successfully"

class FeedbackRequest(BaseModel):
    detection_id: int
    analyst_email: str
    corrected_verdict: Optional[str] = None
    notes: Optional[str] = None
    useful: Optional[bool] = None


class FeedbackResponse(BaseModel):
    feedback_id: int
    message: str = "Feedback stored successfully"


class DetectionComputation(BaseModel):
    risk_score: float
    confidence: float
    verdict: str
    detected_signals: List[DetectedSignal] = Field(default_factory=list)
    reasoning_summary: str
    recommended_action: str
    evidence: Dict[str, Any] = Field(default_factory=dict)
    model_versions: Dict[str, Any] = Field(default_factory=dict)