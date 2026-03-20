from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class EmailSample(SQLModel, table=True):
    __tablename__ = "email_samples"

    id: Optional[int] = Field(default=None, primary_key=True)
    source_type: str = Field(index=True)
    source_name: Optional[str] = None
    subject: Optional[str] = Field(default=None, index=True)
    from_address: Optional[str] = Field(default=None, index=True)
    from_domain: Optional[str] = Field(default=None, index=True)
    reply_to: Optional[str] = None
    message_id: Optional[str] = Field(default=None, index=True)
    received_at: Optional[datetime] = None
    text_body: Optional[str] = None
    html_body: Optional[str] = None
    rendered_screenshot_path: Optional[str] = None
    qr_values: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    attachments: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    metadata: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class Detection(SQLModel, table=True):
    __tablename__ = "detections"

    id: Optional[int] = Field(default=None, primary_key=True)
    email_sample_id: Optional[int] = Field(default=None, foreign_key="email_samples.id", index=True)
    verdict: str = Field(index=True)
    risk_score: float = Field(index=True)
    confidence: float = Field(index=True)
    recommended_action: str
    detected_signals: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    reasoning_summary: str
    evidence: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    model_versions: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    raw_feature_vector: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class AnalystFeedback(SQLModel, table=True):
    __tablename__ = "analyst_feedback"

    id: Optional[int] = Field(default=None, primary_key=True)
    detection_id: int = Field(foreign_key="detections.id", index=True)
    analyst_email: str = Field(index=True)
    corrected_verdict: str = Field(index=True)
    notes: Optional[str] = None
    useful: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class SyntheticSample(SQLModel, table=True):
    __tablename__ = "synthetic_samples"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    scenario_type: str = Field(index=True)
    language: str = Field(default="es")
    sophistication: str = Field(default="medium")
    tone: str = Field(default="urgent")
    content: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    pedagogy: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class BrandProfile(SQLModel, table=True):
    __tablename__ = "brand_profiles"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    official_domains: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    logo_hashes: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    keywords: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AuditLog(SQLModel, table=True):
    __tablename__ = "audit_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    actor: str = Field(index=True)
    action: str = Field(index=True)
    target_type: str = Field(index=True)
    target_id: Optional[str] = Field(default=None, index=True)
    details: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
