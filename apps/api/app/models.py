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