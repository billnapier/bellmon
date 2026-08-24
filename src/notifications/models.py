"""
Pydantic data models for notification payload compilation and delivery tracking.
"""

from typing import Optional, List, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class EmailPayload(BaseModel):
    """Payload representing a compiled responsive HTML email message."""
    recipient_email: str
    recipient_name: Optional[str] = None
    student_name: str
    subject: str
    html_body: str
    text_fallback: str
    missing_work_alerts: List[Any] = Field(default_factory=list)
    grade_drop_alerts: List[Any] = Field(default_factory=list)
    attendance_alerts: List[Any] = Field(default_factory=list)


class DispatchResult(BaseModel):
    """Outcome of an email dispatch attempt via SendGrid or dry-run simulator."""
    success: bool
    message_id: Optional[str] = None
    recipient: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    error_message: Optional[str] = None
    dry_run: bool = False
