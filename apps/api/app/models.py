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