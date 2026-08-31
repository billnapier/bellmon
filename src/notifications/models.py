"""
Pydantic data models for notification payload compilation and delivery tracking.
"""

from typing import Optional, List, Any, Union
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
    """Outcome of an email dispatch attempt via Resend or dry-run simulator."""
    success: bool
    message_id: Optional[str] = None
    recipient: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    error_message: Optional[str] = None
    dry_run: bool = False


class IngestionStatusRecord(BaseModel):
    """Status record of external API ingestion for Canvas or PowerSchool."""
    portal_name: str = "Canvas API"
    status: str = "OPERATIONAL"  # OPERATIONAL, DEGRADED, FAILED
    last_ingested_at: Optional[str] = None
    error_message: Optional[str] = None


class GraceWatchlistItem(BaseModel):
    """Digital missing assignment currently within active grace period."""
    assignment_id: str
    course_id: Optional[str] = None
    course_name: Optional[str] = None
    title: str
    due_at: str
    first_detected_missing: Optional[str] = None
    hours_remaining: float = 0.0


class AttendancePeriodRecord(BaseModel):
    """Single period attendance record for daily summary."""
    period: Union[str, int]
    course_name: Optional[str] = None
    status_code: Optional[str] = "P"
    status: Optional[str] = "PRESENT"
    description: Optional[str] = None


class AttendanceSummary(BaseModel):
    """Daily attendance telemetry summary."""
    date: Optional[str] = None
    records: List[AttendancePeriodRecord] = Field(default_factory=list)
    periods: List[AttendancePeriodRecord] = Field(default_factory=list)
    total_anomalies: int = 0
    total_periods: int = 0
    present_count: int = 0


class HeartbeatPayload(BaseModel):
    """Aggregated daily telemetry payload for system heartbeat briefing email."""
    date: str = ""
    sync_timestamp: Optional[str] = None
    student_id: str = ""
    student_name: str
    canvas_status: str = "OPERATIONAL"
    powerschool_status: str = "OPERATIONAL"
    ingestion_statuses: List[IngestionStatusRecord] = Field(default_factory=list)
    grace_watchlist: List[GraceWatchlistItem] = Field(default_factory=list)
    attendance_summary: Optional[AttendanceSummary] = None
    zero_alert_confirmed: bool = True
    alerts_dispatched_today: int = 0
    critical_alerts_dispatched_today: int = 0


from src.storage.models import HeartbeatDispatchRecord


# Model Aliases for backward/spec compatibility
PortalIngestionRecord = IngestionStatusRecord
DailyAttendanceSummary = AttendanceSummary
